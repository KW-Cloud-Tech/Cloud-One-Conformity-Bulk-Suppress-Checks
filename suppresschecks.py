import os
import argparse
import json
import requests

def parse_args():
    parser = argparse.ArgumentParser(
        description="""Creates a new Conformity profile file from an 
						existing profile, and removes unconfigured rules.""",
    )
    
    # Conformity Region, API Key & Target Account(s) variables (when inputting multiple accounts comma delimit)
    parser.add_argument(
        "-r",
        "--region",
        default="us-west-2",
        required=False,
        help="the region where the Conformity Instance is hosted",
    )
    parser.add_argument(
        "-api",
        "--api_key",
        required=True,
        help="user API key",
    )
    parser.add_argument(
        "-ids",
        "--account_ids",
        default="new_conformity_profile.json",
        required=True,
        help="list of comma separated Conformity account ids",
    )
    
    # Pagination variables
    parser.add_argument(
        "-ps",
        "--page_size",
        default=1000,
        required=False,
        help="the size of the paginated response, defaults to 1000",
    )
    parser.add_argument(
        "-pn",
        "--page_number",
        default=0,
        required=False,
        help="define the page number of the response to return, defaults to 0",
    )
    
    # Suppression note to add
    parser.add_argument(
        "-sn",
        "--suppression_note",
        default="Bulk Suppression Script",
        required=False,
        help="Add a note to the rule configuration change",
    )    
    
    # Checks API Filters
    parser.add_argument(
        "-cat",
        "--filter_categories",
        required=False,
        help="Filter AWS pillar categories: security | cost-optimisation | reliability | performance-efficiency | operational-excellence ",
    )    
    parser.add_argument(
        "-comp",
        "--filter_compliances",
        required=False,
        help="An array of supported standard or framework ids. Possible values: AWAF | CISAWSF | CISAZUREF | CISAWSTTW | PCI | HIPAA | HITRUST | GDPR | APRA | NIST4 | SOC2 | NIST-CSF | ISO27001 | AGISM | ASAE-3150 | MAS"
    )       
    parser.add_argument(
        "-newer",
        "--filter_newerthandays",
        required=False,
        help="Accepts an integer value for number of days",
    ) 
    parser.add_argument(
        "-older",
        "--filter_olderthandays",
        required=False,
        help="Accepts an integer value for number of days",
    )   
    parser.add_argument(
        "-frg",
        "--filter_regions",
        required=False,
        help="Filter checks based on region",
    ) 
    parser.add_argument(
        "-risk",
        "--filter_risklevels",
        required=False,
        help="Filter checks based on risk level, e.g. LOW | MEDIUM | HIGH | VERY_HIGH | EXTREME ",
    ) 
    parser.add_argument(
        "-rule",
        "--filter_ruleids",
        required=False,
        help="Filter checks based on ruleIds",
    ) 
    parser.add_argument(
        "-serv",
        "--filter_services",
        required=False,
        help="Filter checks based on AWS service, e.g. CloudWatchLogs | Config | DynamoDB | EBS | EC2 etc.",
    ) 
    parser.add_argument(
        "-stat",
        "--filter_statuses",
        required=False,
        help="Filter checks based on SUCCESS or FAILURE",
    ) 
    parser.add_argument(
        "-sup",
        "--filter_suppressed",
        required=False,
        help="Filter checks based on whether they are suppressed, e.g. true or false",
    ) 
    parser.add_argument(
        "-sfm",
        "--filter_suppressedfiltermode",
        required=False,
        help="Options are v1 or v2, defaults to v1 | v1: Using suppressed=true will return both suppressed and unsuppressed checks, suppressed=false will just return unsuppressed checks | v2: Using suppressed=true return will just return suppressed checks",
    ) 
    parser.add_argument(
        "-tag",
        "--filter_tags",
        required=False,
        help="Filter checks based on tags",
    ) 

	return parser.parse_args()
    
def main ():
        
	args = parse_args()

	# Set variables
	CC_REGION = args.region
	CC_APIKEY = args.api_key
	CC_ACCOUNTIDS = args.account_ids
	CC_PAGESIZE = int(os.environ.get("CC_PAGESIZE", 1000))
	CC_PAGENUMBER = int(os.environ.get("CC_PAGENUMBER", 0))
	CC_SUPPRESSION_NOTE = os.environ.get("CC_SUPPRESSION_NOTE", "Bulk Suppression Script")
	CC_FILTER_CATEGORIES = args.filter_categories
	CC_FILTER_COMPLIANCES = args.filter_coimpliances
	CC_FILTER_NEWERTHANDAYS = args.filter_newerthandays
	CC_FILTER_OLDERTHANDAYS = args.filter_olderthandays
	CC_FILTER_REGIONS = args.filter_regions
	CC_FILTER_RISKLEVELS = args.filter_risklevels
	CC_FILTER_RULEIDS = args.filter_ruleids
	CC_FILTER_SERVICES = args.filter_services
	CC_FILTER_STATUSES = args.filter_statuses
	CC_FILTER_SUPPRESSED = args.filter_suppressed
	CC_FILTER_SUPPRESSEDFILTERMODE = args.filter_suppressedfiltermode
	CC_FILTER_TAGS = args.filter_tags    

    # Pass arguments in to API call
	url = "https://" + CC_REGION + "-api.cloudconformity.com/v1/checks"
	params = {
		"accountIds": CC_ACCOUNTIDS,
		"filter[categories]": CC_FILTER_CATEGORIES,
		"filter[compliances]": CC_FILTER_COMPLIANCES,
		"filter[newerThanDays]": CC_FILTER_NEWERTHANDAYS,
		"filter[olderThanDays]": CC_FILTER_OLDERTHANDAYS,
		"filter[regions]": CC_FILTER_REGIONS,
		"filter[riskLevels]": CC_FILTER_RISKLEVELS,
		"filter[ruleIds]": CC_FILTER_RULEIDS,
		"filter[services]": CC_FILTER_SERVICES,
		"filter[tags]": CC_FILTER_TAGS,
		"filter[statuses]": CC_FILTER_STATUSES,
		"filter[suppressed]": CC_FILTER_SUPPRESSED,
		"filter[suppressedFilterMode]": CC_FILTER_SUPPRESSEDFILTERMODE,
		"page[size]": CC_PAGESIZE,
		"page[number]": CC_PAGENUMBER,
	}

    payload = {}
    headers = {
        "Content-Type": "application/vnd.api+json",
        "Authorization": "ApiKey " + CC_APIKEY,
    }

    session = requests.session()    
    
    def get_account_checks():

        combined = []
        counter = 0
        max_results = 1
        while counter <= max_results:
            page = session.get(url, params=params, headers=headers, data=payload).json()
            max_results = page["meta"]["total"]
            counter += CC_PAGESIZE
            params["page[number]"] += 1
            data = page["data"]
            combined += data
        return {"data": combined, "meta": page["meta"]}

    pages_combined = get_account_checks()
    checkstosuppress = pages_combined["data"]
    for check in checkstosuppress:
        id = check["id"]
        checkurl = url + "/" + id
        suppressbody = {
            "data": {
                "type": "checks",
                "attributes": {"suppressed": True, "suppressed-until": None},
            },
            "meta": {"note": CC_SUPPRESSION_NOTE},
        }
        jsonbody = json.dumps(suppressbody)
        suppress = session.patch(checkurl, headers=headers, data=jsonbody)
        print(
            "Received API response code of "
            + str(suppress.status_code)
            + " for suppression of check ID: "
            + id
        )
