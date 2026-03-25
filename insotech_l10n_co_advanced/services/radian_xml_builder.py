# -*- coding: utf-8 -*-
"""RADIAN ApplicationResponse XML Builder.

Generates the UBL 2.1 XML for Events 030, 032, 033, 034, 035.
"""

import hashlib
from datetime import datetime

def compute_radian_cude(num_ar, fec_ar, hor_ar, nit_ofe, nit_adq, cod_evento, cufe_padre, pin_software):
    """Calcula el CUDE de un Evento RADIAN según Anexo Técnico 1.9."""
    cude_string = f"{num_ar}{fec_ar}{hor_ar}{nit_ofe}{nit_adq}{cod_evento}{cufe_padre}{pin_software}"
    return hashlib.sha384(cude_string.encode('utf-8')).hexdigest()

def _compute_dv(nit_str):
    """Calcula dígito de verificación DIAN (Módulo 11) para un NIT."""
    if not nit_str or not str(nit_str).isdigit():
        return '0'
    factors = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
    nit_str = str(nit_str).zfill(15)
    total = sum(int(digit) * factors[i] for i, digit in enumerate(reversed(nit_str)))
    remainder = total % 11
    return str(11 - remainder) if remainder >= 2 else str(remainder)

def _get_claim_description(code):
    if code == '01': return 'Documento con inconsistencias'
    if code == '02': return 'Mercancía no entregada totalmente'
    if code == '03': return 'Mercancía no entregada parcialmente'
    if code == '04': return 'Servicio no prestado'
    return 'Reclamo'

def generate_application_response(event):
    """Genera el XML UBL 2.1 para el evento RADIAN especificado."""
    move = event.move_id
    company = event.company_id
    partner = move.company_id.partner_id
    
    # Prefix mapping for unique ID
    prefixes = {
        '030': 'ACR',
        '032': 'RMD',
        '033': 'AEX',
        '034': 'RCL',
        '031': 'REJ',
        '035': 'ATC',
    }
    
    # Text descriptions
    descriptions = {
        '030': 'Acuse de recibo de Factura Electrónica de Venta',
        '032': 'Recibo de bien y/o prestación del servicio',
        '033': 'Aceptación expresa de la factura electrónica de venta',
        '034': 'Reclamo de la Factura Electrónica de Venta',
        '031': 'Rechazo de la factura electrónica de venta',
        '035': 'Aceptación Tácita de la factura electrónica de venta',
    }
    
    prefix = prefixes.get(event.event_code, 'RAD')
    event_num = str(event.id).zfill(6)
    ar_id = f"{prefix}{event_num}"
    
    event_dt = event.event_date
    fec_ar = event_dt.strftime('%Y-%m-%d')
    hor_ar = event_dt.strftime('%H:%M:%S-05:00')
    
    # Emitida por el Facturador (Seller, NitOFE). Adquiriente (Buyer, NitAdq).
    nit_ofe = partner.vat or ''
    nit_adq = company.vat or ''
    
    dv_ofe = _compute_dv(nit_ofe)
    dv_adq = _compute_dv(nit_adq)
    
    software_pin = company.insotech_dian_software_pin or ''
    software_id = company.insotech_dian_software_id or ''
    
    cufe_padre = move.l10n_co_edi_cufe_cude_ref or ''
    invoice_number = move.name or ''
    
    # Calculate CUDE
    cude = compute_radian_cude(
        num_ar=ar_id,
        fec_ar=fec_ar,
        hor_ar=hor_ar,
        nit_ofe=nit_ofe,
        nit_adq=nit_adq,
        cod_evento=event.event_code,
        cufe_padre=cufe_padre,
        pin_software=software_pin
    )
    
    profile_id = 'DIAN 2.1: ApplicationResponse de la Factura Electrónica de Venta'
    response_code = event.event_code
    response_desc = descriptions.get(event.event_code, '')
    
    # Add Claim Code block if this is a Reclamo 034
    line_response_xml = ""
    if event.event_code == '034' and event.claim_code:
        claim_desc = _get_claim_description(event.claim_code)
        line_response_xml = f"""
        <cac:LineResponse>
            <cac:LineReference>
                <cbc:LineID>1</cbc:LineID>
            </cac:LineReference>
            <cac:Response>
                <cbc:ResponseCode>{event.claim_code}</cbc:ResponseCode>
                <cbc:Description>{claim_desc}</cbc:Description>
            </cac:Response>
        </cac:LineResponse>
        """
        
    xml_template = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<ApplicationResponse xmlns="urn:oasis:names:specification:ubl:schema:xsd:ApplicationResponse-2"
        xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
        xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
        xmlns:ds="http://www.w3.org/2000/09/xmldsig#"
        xmlns:ext="urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
        xmlns:sts="dian:gov:co:facturaelectronica:Structures-2-1"
        xmlns:xades="http://uri.etsi.org/01903/v1.3.2#"
        xmlns:xades141="http://uri.etsi.org/01903/v1.4.1#"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="urn:oasis:names:specification:ubl:schema:xsd:ApplicationResponse-2 http://docs.oasis-open.org/ubl/os-UBL-2.1/xsd/maindoc/UBL-ApplicationResponse-2.1.xsd">
    <ext:UBLExtensions>
        <ext:UBLExtension>
            <ext:ExtensionContent>
                <sts:DianExtensions>
                    <sts:InvoiceSource>
                        <cbc:IdentificationCode listAgencyID="6" listAgencyName="United Nations Economic Commission for Europe" listSchemeURI="urn:oasis:names:specification:ubl:codelist:gc:CountryIdentificationCode-2.1">CO</cbc:IdentificationCode>
                    </sts:InvoiceSource>
                    <sts:SoftwareProvider>
                        <sts:ProviderID schemeID="{dv_adq}" schemeName="31" schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)">{nit_adq}</sts:ProviderID>
                        <sts:SoftwareID schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)">{software_id}</sts:SoftwareID>
                    </sts:SoftwareProvider>
                    <sts:SoftwareSecurityCode schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)">{cude}</sts:SoftwareSecurityCode>
                    <sts:AuthorizationProvider>
                        <sts:AuthorizationProviderID schemeID="4" schemeName="31" schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)">800197268</sts:AuthorizationProviderID>
                    </sts:AuthorizationProvider>
                    <sts:QRCode>https://catalogo-vpfe.dian.gov.co/document/searchqr?documentkey={cufe_padre}</sts:QRCode>
                </sts:DianExtensions>
            </ext:ExtensionContent>
        </ext:UBLExtension>
        <ext:UBLExtension>
            <ext:ExtensionContent>
<!-- ds:Signature -->
            </ext:ExtensionContent>
        </ext:UBLExtension>
    </ext:UBLExtensions>
    <cbc:UBLVersionID>UBL 2.1</cbc:UBLVersionID>
    <cbc:CustomizationID>1</cbc:CustomizationID>
    <cbc:ProfileID>{profile_id}</cbc:ProfileID>               
    <cbc:ProfileExecutionID>2</cbc:ProfileExecutionID>
    <cbc:ID>{ar_id}</cbc:ID>
    <cbc:UUID schemeID="2" schemeName="CUDE-SHA384">{cude}</cbc:UUID>
    <cbc:IssueDate>{fec_ar}</cbc:IssueDate>
    <cbc:IssueTime>{hor_ar}</cbc:IssueTime>
    <cbc:Note>{ar_id}{fec_ar}{hor_ar}{nit_ofe}{nit_adq}{response_code}{cufe_padre}{software_pin}</cbc:Note>
    <cac:SenderParty>
        <cac:PartyTaxScheme>
            <cbc:RegistrationName>{company.name}</cbc:RegistrationName>
            <cbc:CompanyID schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)" schemeID="{dv_adq}" schemeName="31" schemeVersionID="1">{nit_adq}</cbc:CompanyID>
            <cac:TaxScheme>                                      
                <cbc:ID>01</cbc:ID>
                <cbc:Name>IVA</cbc:Name>
            </cac:TaxScheme>
        </cac:PartyTaxScheme>
    </cac:SenderParty>
    <cac:ReceiverParty>
        <cac:PartyTaxScheme>
            <cbc:RegistrationName>{partner.name}</cbc:RegistrationName>
            <cbc:CompanyID schemeAgencyID="195" schemeAgencyName="CO, DIAN (Dirección de Impuestos y Aduanas Nacionales)" schemeID="{dv_ofe}" schemeName="31" schemeVersionID="1">{nit_ofe}</cbc:CompanyID>
            <cac:TaxScheme>
                <cbc:ID>01</cbc:ID>
                <cbc:Name>IVA</cbc:Name>
            </cac:TaxScheme>
        </cac:PartyTaxScheme>
    </cac:ReceiverParty>
    <cac:DocumentResponse>
        <cac:Response>
            <cbc:ResponseCode>{response_code}</cbc:ResponseCode>
            <cbc:Description>{response_desc}</cbc:Description>
        </cac:Response>
        <cac:DocumentReference>
            <cbc:ID>{invoice_number}</cbc:ID>
            <cbc:UUID schemeName="CUFE-SHA384">{cufe_padre}</cbc:UUID>
            <cbc:DocumentTypeCode>01</cbc:DocumentTypeCode>
        </cac:DocumentReference>
        <cac:IssuerParty>
            <cac:Person>
                <cbc:ID schemeID="4" schemeName="13">{company.vat}</cbc:ID>
                <cbc:FirstName>{company.name}</cbc:FirstName>
                <cbc:FamilyName></cbc:FamilyName>
                <cbc:JobTitle>Representante Legal</cbc:JobTitle>
                <cbc:OrganizationDepartment>Juridica</cbc:OrganizationDepartment>
            </cac:Person>
        </cac:IssuerParty>
        {line_response_xml}
    </cac:DocumentResponse>
</ApplicationResponse>
"""
    return xml_template
