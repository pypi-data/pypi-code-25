ccs_template = '''
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:web="https://nww.pathwaysdos.nhs.uk/app/api/webservices">
<soap:Header>
<web:serviceVersion>1.3</web:serviceVersion>
</soap:Header>
<soap:Body>
<web:CheckCapacitySummary>
<web:userInfo>
<web:username>{0}</web:username>
<web:password>{1}</web:password>
</web:userInfo>
<web:c>
<!--Optional:-->
<web:caseRef>{2}</web:caseRef>
<!--Optional:-->
<web:caseId>{3}</web:caseId>
<web:postcode>{4}</web:postcode>
<!--Optional:-->
<web:surgery>{5}</web:surgery>
<web:age>{6}</web:age>
<web:ageFormat>{7}</web:ageFormat>
<web:disposition>{8}</web:disposition>
<web:symptomGroup>{9}</web:symptomGroup>
<web:symptomDiscriminatorList>
<web:int>{10}</web:int>
</web:symptomDiscriminatorList>
<!--Optional:-->
<web:searchDistance>{11}</web:searchDistance>
<web:gender>{12}</web:gender>
</web:c>
</web:CheckCapacitySummary>
</soap:Body>
</soap:Envelope>
'''


def generate_ccs_payload(user, case):

    ccs_body = ccs_template.format(
        user.username,
        user.password,
        case.case_ref,
        case.case_id,
        case.postcode,
        case.surgery,
        case.age,
        case.age_format,
        case.disposition,
        case.symptom_group,
        case.symptom_discriminator,
        case.search_distance,
        case.sex,
    )

    return ccs_body
