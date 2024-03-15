import re
import socket
import ssl

import requests
import urllib3
from requests.exceptions import MissingSchema

TYPE_KEY = 'content-type'
LENGTH_KEY = 'content-length'
CONT_DISP = 'content-disposition'
F_PAT = re.compile(r'filename=(.+)')
FOLDERS_PATTERN = re.compile(r'([0-9]+)[^a-z0-9]*(.*)')
GET_EXCEPT = (MissingSchema, ssl.SSLCertVerificationError,
              requests.exceptions.SSLError, AttributeError,
              requests.exceptions.TooManyRedirects,
              requests.exceptions.ConnectionError,
              requests.exceptions.MissingSchema,
              requests.exceptions.InvalidURL, socket.gaierror,
              urllib3.exceptions.SSLError,
              urllib3.exceptions.NewConnectionError,
              urllib3.exceptions.LocationParseError,
              urllib3.exceptions.MaxRetryError,
              urllib3.exceptions.NameResolutionError,)
DO_NOT_GO_TO_PLACES_ENDING_IN = (
    '.jpg',
    '.mp3',
    '.pdf',
    '.png',
    '.pptx',
    '.txt',
    '.wav',
)
DO_NOT_GO_TO_PLACES_CONTAINING = (
    '-account',
    '-administra',
    '-audio',
    '-award',
    '-bullet',
    '-business',
    '-charge',
    '-direction',
    '-disaster',
    '-engagement',
    '-experience',
    '-framework',
    '-fund',
    '-gover',
    '-guide',
    '-hearings.htm',
    '-impact',
    '-in-your-language',
    '-initiative',
    '-island',
    '-legislation',
    '-licen',
    '-management',
    '-network',
    '-options',
    '-package',
    '-partnership',
    '-phase',
    '-pilot',
    '-plan',
    '-program',
    '-question',
    '-radio',
    '-reference',
    '-reform',
    '-regulation',
    '-scheme',
    '-service',
    '-shipping',
    '-standard',
    '-tenancy',
    '-trial',
    '-vehicle',
    '-winner',
    '.ahc.sa.gov',
    '.com',
    '.legislation.',
    '.ombudsman.',
    '.org.uk',
    '.transport.',
    '.w3.org',
    'aapant.org',
    'about-',
    'about_aec',
    'about_us',
    'aboutus',
    'accessibility.html',
    'actcoss.org',
    'actleave.act',
    'adelaidefringe',
    'air-freight',
    'air-traffic',
    'airport',
    'alawa.org',
    'alc.org',
    'alexandrina.sa.gov.',
    'alicesprings.nt',
    'apache.org',
    'apc.sa.gov',
    'app-store',
    'applications-refused',
    'appointment-of-chairperson.htm',
    'arnhem.nt',
    'artwork',
    'ask-ecsa',
    'ato.gov',
    'audit.act',
    'austroads',
    'autlii.edu',
    'aviation',
    'barkly.nt',
    'barungawest.sa.gov',
    'batchelor.edu',
    'belyuen.nt',
    'berribarmera.sa.gov',
    'brochure.html',
    'brochures-',
    'burnside.sa.gov',
    'business.act',
    'call-for-submissions',
    'campbelltown.sa.gov',
    'canberrahealthservices.act',
    'ceduna.sa.gov',
    'centraldesert.nt',
    'charlessturt.sa.gov',
    'check-my-enrolment',
    'cit.edu',
    'cityofadelaide',
    'cityofpae.sa.gov',
    'ckan.org',
    'claim-processing',
    'claregilbertvalleys.sa.gov',
    'cleve.sa.gov',
    'cmtedd.act',
    'constitutional-amendments.html',
    'contact-',
    'contact_us',
    'coomalie.nt',
    'coorong.sa.gov',
    'coppercoast.sa.gov',
    'copyright.htm',
    'coronavirus.nt',
    'corporate-',
    'corridor-strategy',
    'council-meeting',
    'courts.sa.gov',
    'creativecommons.org',
    'criminal-justice',
    'culturalfacilities.act',
    'dangerous-good',
    'darwin.nt',
    'detail?county=1',
    'devfacebookprovider',
    'digi.me',
    'disclaimer.htm',
    'disclosures.ecsa',
    'disinformation-register.htm',
    'dismax-query-parser',
    'dismaxqueryparser',
    'diversityandinclusion',
    'djilpinarts.org',
    'drupal.org',
    'ecanz.gov',
    'education.act',
    'elliston.sa.gov',
    'enforcement-',
    'enrol',
    'envcomm.act',
    'environment.act',
    'esa.act',
    'eventbrite',
    'exhibits.html',
    'experienceadelaide',
    'feedback-and-complaints',
    'fines.sa.gov',
    'forgotpassword',
    'form=shop',
    'form=shpnlb',
    'form?efrm=af',
    'forms.pfes',
    'formupload',
    'fraud.htm',
    'ftp:',
    'funding-deadline',
    'gamblershelp',
    'gamblingandracing.act',
    'gamblinghelponline',
    'gamblingsupport.org',
    'github.',
    'glossary.htm',
    'govt.nz',
    'goyder.sa.gov',
    'grants.act',
    'guide-for',
    'guidelines',
    'healthdirect.gov',
    'homeaffairs.gov',
    'homevaluation',
    'how-to-',
    'how_to_',
    'icac.sa.gov',
    'ico.org',
    'icrc.act',
    'ics.act',
    'import-',
    'imprint.html',
    'infrastructure-',
    'inspector.sa.gov',
    'integrity.act',
    'javascript:',
    'jobs.act',
    'journey-guide',
    'kabcnt.org',
    'katherine.nt',
    'ktc.nt',
    'language-resources',
    'languages2',
    'law.gov',
    'leagalaidact.org',
    'legislation.act',
    'legislation.nt',
    'licence-applications',
    'lichfield.nt',
    'light.sa.gov',
    'login',
    'loxtonwaikerie',
    'macdonnell.nt',
    'mailto:',
    'majurapines.org',
    'maritime-',
    'marpol',
    'media-centre',
    'mid-murray.sa.gov',
    'ministerial-',
    'mitchamcouncil.sa.gov',
    'mountbarker.sa.gov',
    'mountgambier.sa.gov',
    'mozilla.org',
    'mtr.sa.gov',
    'murraybridge.sa.gov',
    'myaccount',
    'naracoortelucindale.sa.gov',
    'nasa.gov',
    'nationalarboretum.act',
    'new-citizens.htm',
    'newhomes',
    'nla.gov',
    'nlc.org',
    'npsp.sa.gov',
    'ntconcessions.net',
    'ntconcessions.nt',
    'onecard.network',
    'org.nz',
    'osdm.gov',
    'our-partners',
    'our-vision',
    'ovs.act',
    'ownership-control',
    'palmerston.nt',
    'parks.act',
    'pirie.sa.gov',
    'plan.sa.gov',
    'policy-statement',
    'portaugusta.sa.gov',
    'privacy-statement',
    'privacy.htm',
    'privacynotice',
    'project-delivery',
    'prospect.sa.gov',
    'publicintegrity.sa.gov',
    'publictrustee.act',
    'raveis',
    'recusal-of-chairperson.html',
    'redistributions.html?layout=table',
    'regeneratingalice',
    'register-',
    'regulation-',
    'relayservice.gov',
    'renmarkparinga.sa.gov',
    'resources-meta',
    'rethinkaddiction.org',
    'road-rules',
    'roadmap-',
    'roads-publications',
    'robe.sa.gov',
    'ropergulf.nt',
    'royal-elemen',
    'rundelemall',
    'sahealth.sa',
    'salisbury.sa.gov',
    'salvationarmy.org',
    'scienceweek.net',
    'search',
    'shop.',
    'shop?',
    'sign_in',
    'sign_up',
    'signin',
    'southernmallee.sa.gov',
    'spatial.gov',
    'strategic-assessment',
    'streakybay.sa.gov',
    'submissions.htm',
    'suburbanland.act',
    'supply-chain',
    'tel:',
    'termsandconditions',
    'tickets',
    'timetable.html',
    'tisnational.gov',
    'tiwsisslands.org',
    'tlavs',
    'torproject.org',
    'tqi.act',
    'translated_information',
    'transport-',
    'trs.border',
    'trust-and-satisfaction.htm',
    'twitter',
    'twtr-main',
    'verifymyaccount',
    'victoriadaly.nt',
    'virtualenv.org',
    'vote.nz',
    'voyage_reports',
    'wakefieldrc.sa'
    'waterconnect.sa',
    'ways_to_vote',
    'websitetermsofuse',
    'webtobeck.tk',
    'westarnhem.nt',
    'westdaly.nt',
    'wgait.nt',
    'whyalla.sa.gov',
    'wordpress.org',
    'working-at-elections',
    'yorke.sa.gov',
    'youronlinechoices',
)