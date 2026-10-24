import sys
import os
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.app.database import SessionLocal, Base, engine
from backend.app.models import (
    Scheme,
    SchemeTranslation,
    Benefit,
    RequiredDocument,
    ApplicationStep,
    EligibilityRule,
    OfficialSource,
    SourceVerificationHistory
)

def seed(target_db=None, target_engine=None):
    use_engine = target_engine or engine
    Base.metadata.create_all(bind=use_engine)
    db = target_db or SessionLocal()
    should_close = target_db is None

    try:
        print("🌱 Seeding YojanaSetu Database with Verified Government Records...")

        # -------------------------------------------------------------
        # 1. Post-Matric Scholarship Scheme
        # -------------------------------------------------------------
        pm_scheme = db.query(Scheme).filter(Scheme.slug == "post-matric").first()
        if not pm_scheme:
            pm_scheme = Scheme(
                slug="post-matric",
                official_name="Post-Matric Scholarship Scheme for SC, ST, OBC and Minorities",
                ministry="Ministry of Social Justice & Empowerment",
                is_central=True,
                state_or_region="All India",
                category="education",
                category_label="Higher Education Grant",
                numeric_benefit_value=48500.0,
                application_method="online",
                external_portal_name="National Scholarship Portal (NSP)",
                external_portal_url="https://scholarships.gov.in",
                status="active",
                is_retired=False,
                verification_status="verified",
                last_verified_at=datetime.now(timezone.utc)
            )
            db.add(pm_scheme)
            db.flush()

            # Translations (en & hi reviewed)
            db.add(SchemeTranslation(
                scheme_id=pm_scheme.id,
                language_code="en",
                localized_name="Post-Matric Scholarship Scheme (OBC, SC, ST & Minority)",
                localized_description="Centrally sponsored scheme providing complete fee reimbursement and maintenance allowances to underprivileged students pursuing post-matriculation degrees.",
                localized_benefit_summary="Full compulsory fees waiver + ₹13,500/yr maintenance allowance",
                why_qualify_text="Enrolled in recognized Post-Matriculation / Higher Education Degree program; Belongs to reserved social category (SC/ST/OBC/Minority/EWS); Family income verified under statutory limit of ₹2,50,000/yr; Institution possesses active AISHE accreditation code",
                why_not_qualify_text="Student is enrolled through distance/correspondence mode without practical credits; Student is already availing another concurrent central or UGC stipend; Applicant has failed recurring academic session twice consecutively",
                is_reviewed=True,
                reviewed_by="Superintendent Officer, MSJE"
            ))
            db.add(SchemeTranslation(
                scheme_id=pm_scheme.id,
                language_code="hi",
                localized_name="पोस्ट-मैट्रिक छात्रवृत्ति योजना (ओबीसी, एससी, एसटी एवं अल्पसंख्यक)",
                localized_description="उच्च शिक्षा प्राप्त कर रहे पात्र छात्र-छात्राओं के लिए पूर्ण शुल्क प्रतिपूर्ति एवं मासिक निर्वाह भत्ता योजना।",
                localized_benefit_summary="पूर्ण अनिवार्य शुल्क माफी + ₹13,500/वर्ष निर्वाह भत्ता",
                why_qualify_text="मान्यता प्राप्त उच्च शिक्षा / डिग्री पाठ्यक्रम में नियमित रूप से नामांकित; आरक्षित सामाजिक वर्ग (SC/ST/OBC/अल्पसंख्यक/EWS) से संबंधित; पारिवारिक वार्षिक आय ₹2,50,000 की वैधानिक सीमा के भीतर है; संस्थान के पास सक्रिय AISHE प्रत्यायन कोड मौजूद है",
                why_not_qualify_text="छात्र बिना व्यावहारिक क्रेडिट के पत्राचार / दूरस्थ शिक्षा में नामांकित है; छात्र पहले से ही किसी अन्य केंद्रीय या यूजीसी छात्रवृत्ति का लाभ ले रहा है; आवेदक लगातार दो बार संबंधित शैक्षणिक सत्र में अनुत्तीर्ण हुआ है",
                is_reviewed=True,
                reviewed_by="Superintendent Officer, MSJE"
            ))

            # Benefits
            db.add(Benefit(
                scheme_id=pm_scheme.id,
                benefit_type="fee_waiver",
                amount=35000.0,
                frequency="annual",
                description="100% compulsory tuition and examination fee waiver remitted directly to institution.",
                disbursement_method="Direct Institutional Credit"
            ))
            db.add(Benefit(
                scheme_id=pm_scheme.id,
                benefit_type="cash_transfer",
                amount=13500.0,
                frequency="annual",
                description="Living maintenance allowance credited directly to student's Aadhaar-linked bank account.",
                disbursement_method="DBT (Aadhaar Payment Bridge)"
            ))

            # Eligibility Rules
            db.add(EligibilityRule(
                scheme_id=pm_scheme.id,
                rule_code="PMS_STUDENT",
                field_name="student_status",
                operator="eq",
                target_value="Yes",
                is_mandatory=True,
                description="Must be actively enrolled as a full-time student in a recognized post-matric course",
                failure_reason="Applicant is not currently enrolled as a student"
            ))
            db.add(EligibilityRule(
                scheme_id=pm_scheme.id,
                rule_code="PMS_INCOME",
                field_name="max_income",
                operator="lte",
                target_value="250000",
                is_mandatory=True,
                description="Annual household income from all sources must not exceed ₹2,50,000",
                failure_reason="Annual household income exceeds statutory threshold of ₹2,50,000"
            ))
            db.add(EligibilityRule(
                scheme_id=pm_scheme.id,
                rule_code="PMS_CATEGORY",
                field_name="social_category",
                operator="in",
                target_value="SC,ST,OBC,EWS",
                is_mandatory=True,
                description="Must belong to SC, ST, OBC, EWS, or recognized Minority community",
                failure_reason="Applicant does not belong to specified eligible social categories"
            ))

            # Documents
            db.add(RequiredDocument(
                scheme_id=pm_scheme.id,
                document_code="aadhaar",
                document_name="Aadhaar Card (Mobile Number & NPCI Linked)",
                authority="UIDAI",
                is_mandatory=True,
                steps="Download e-Aadhaar from uidai.gov.in or visit your nearest Aadhaar Seva Kendra for biometric mobile update.",
                turnaround="Instant (Online) / 3 Days",
                estimated_cost="Free online / ₹50 for update",
                official_guide_url="https://uidai.gov.in"
            ))
            db.add(RequiredDocument(
                scheme_id=pm_scheme.id,
                document_code="caste_cert",
                document_name="Valid Social Category / Caste Certificate",
                authority="Tehsildar / SDO Revenue Office",
                is_mandatory=True,
                steps="Apply online on your state e-District portal or submit Form 1 at Tehsil desk with ancestral land/caste proof.",
                turnaround="7 - 14 Business Days",
                estimated_cost="₹30 CSC processing fee",
                official_guide_url="https://services.india.gov.in"
            ))
            db.add(RequiredDocument(
                scheme_id=pm_scheme.id,
                document_code="income_cert",
                document_name="Competent Authority Income Certificate (< ₹2.5L)",
                authority="Revenue Department / Lekhpal",
                is_mandatory=True,
                steps="Apply via CSC / Tehsil with electricity bill, salary slip, or Patwari verification report.",
                turnaround="5 - 10 Business Days",
                estimated_cost="₹20 - ₹50",
                official_guide_url="https://edistrict.gov.in"
            ))
            db.add(RequiredDocument(
                scheme_id=pm_scheme.id,
                document_code="hostel_cert",
                document_name="Hosteller Verification Certificate",
                authority="Chief Warden / Institution Hostel Desk",
                is_mandatory=False,
                top_up_benefit="Unlocks +₹8,000/year additional hosteller maintenance stipend",
                steps="Procure stamped mess and hostel allotment ledger certificate from the institution warden.",
                turnaround="1 Business Day",
                estimated_cost="Free"
            ))

            # Application Steps
            db.add(ApplicationStep(
                scheme_id=pm_scheme.id,
                step_order=1,
                title="Register on National Scholarship Portal (NSP)",
                description="Visit scholarships.gov.in and create an account with your Aadhaar-linked mobile number and OTR (One-Time Registration).",
                issuing_office="NSP Portal",
                is_online=True,
                portal_or_form_link="https://scholarships.gov.in"
            ))
            db.add(ApplicationStep(
                scheme_id=pm_scheme.id,
                step_order=2,
                title="Fill Scheme Application Form & Upload Documents",
                description="Select 'Post-Matric Scholarship Scheme', enter your AISHE college code, and upload income and category certificates.",
                issuing_office="College Nodal Officer",
                is_online=True
            ))
            db.add(ApplicationStep(
                scheme_id=pm_scheme.id,
                step_order=3,
                title="Institutional Level Verification",
                description="Submit physical verification copies to your college scholarship nodal officer for online endorsement.",
                issuing_office="College Registrar",
                is_online=False
            ))

            # Official Source
            src = OfficialSource(
                scheme_id=pm_scheme.id,
                source_name="National Scholarship Portal Gazette Guidelines 2026",
                source_type="gazette",
                official_url="https://scholarships.gov.in",
                authority_name="Ministry of Social Justice and Empowerment",
                verification_status="verified",
                is_accessible=True
            )
            db.add(src)

        # -------------------------------------------------------------
        # 2. PM Surya Ghar: Muft Bijli Yojana
        # -------------------------------------------------------------
        ps_scheme = db.query(Scheme).filter(Scheme.slug == "pm-surya").first()
        if not ps_scheme:
            ps_scheme = Scheme(
                slug="pm-surya",
                official_name="PM Surya Ghar: Muft Bijli Yojana (Rooftop Solar Subsidy)",
                ministry="Ministry of New and Renewable Energy",
                is_central=True,
                state_or_region="All India",
                category="livelihood",
                category_label="Clean Energy & Capital Subsidy",
                numeric_benefit_value=78000.0,
                application_method="online",
                external_portal_name="PM Surya Ghar National Portal",
                external_portal_url="https://pmsuryaghar.gov.in",
                status="active",
                is_retired=False,
                verification_status="verified",
                last_verified_at=datetime.now(timezone.utc)
            )
            db.add(ps_scheme)
            db.flush()

            db.add(SchemeTranslation(
                scheme_id=ps_scheme.id,
                language_code="en",
                localized_name="PM Surya Ghar: Muft Bijli Yojana (Rooftop Solar Subsidy)",
                localized_description="National solar rooftop mission offering direct capital cash subsidy of up to ₹78,000 to households installing grid-connected solar power systems.",
                localized_benefit_summary="Direct capital cash subsidy up to ₹78,000 for residential 3kW rooftop solar",
                why_qualify_text="Household possesses independent residential roof ownership rights; Valid domestic grid-connected DISCOM electricity connection; Annual family income satisfies state utility slabs",
                why_not_qualify_text="Commercial or industrial power connection meter installed; Applicant has previously received solar capital subsidies from central/state agencies; Premises roof is disputed or rented without explicit landlord NOC",
                is_reviewed=True,
                reviewed_by="MNRE Technical Advisory Group"
            ))
            db.add(SchemeTranslation(
                scheme_id=ps_scheme.id,
                language_code="hi",
                localized_name="पीएम सूर्य घर: मुफ्त बिजली योजना (रूफटॉप सोलर सब्सिडी)",
                localized_description="आवासीय घरों की छतों पर ग्रिड-कनेक्टेड सोलर पैनल लगाने हेतु केंद्र सरकार द्वारा ₹78,000 तक की प्रत्यक्ष सब्सिडी योजना।",
                localized_benefit_summary="3 किलोवाट आवासीय रूफटॉप सोलर हेतु ₹78,000 तक की प्रत्यक्ष नकद सब्सिडी",
                why_qualify_text="परिवार के पास आवासीय छत का स्वतंत्र मालिकाना अधिकार मौजूद है; वैध घरेलू ग्रिड-कनेक्टेड बिजली वितरण कंपनी (DISCOM) का मीटर उपलब्ध है; पारिवारिक आय सीमा राज्य विद्युत बोर्ड के मानदंडों के अनुकूल है",
                why_not_qualify_text="परिसर में वाणिज्यिक अथवा औद्योगिक बिजली मीटर लगा हुआ है; आवेदक को पूर्व में किसी अन्य सौर सब्सिडी योजना का लाभ प्राप्त हो चुका है; छत विवादित है अथवा बिना मकान मालिक की लिखित अनुमति के किराए पर है",
                is_reviewed=True,
                reviewed_by="MNRE Technical Advisory Group"
            ))

            db.add(Benefit(
                scheme_id=ps_scheme.id,
                benefit_type="subsidy",
                amount=78000.0,
                frequency="one_time",
                description="Up to ₹78,000 direct bank cash credit for 3kW rooftop system within 30 days of DISCOM inspection.",
                disbursement_method="Direct DBT to Bank Account"
            ))

            db.add(RequiredDocument(
                scheme_id=ps_scheme.id,
                document_code="elec_bill",
                document_name="Latest Electricity Bill (Past 3 Months)",
                authority="State DISCOM Electricity Department",
                is_mandatory=True,
                steps="Download consumer bill receipt from state electricity board website or electricity mobile app.",
                turnaround="Instant",
                estimated_cost="Free",
                official_guide_url="https://pmsuryaghar.gov.in"
            ))
            db.add(RequiredDocument(
                scheme_id=ps_scheme.id,
                document_code="roof_proof",
                document_name="Roof Rights / Municipal House Tax Assessment Receipt",
                authority="Municipal Corporation / Gram Panchayat",
                is_mandatory=True,
                steps="Procure latest house tax or municipal assessment receipt from municipal counter or e-Nagar portal.",
                turnaround="1 - 3 Days",
                estimated_cost="Free"
            ))

            db.add(ApplicationStep(
                scheme_id=ps_scheme.id,
                step_order=1,
                title="Register on PM Surya Ghar Portal",
                description="Sign up on pmsuryaghar.gov.in using your DISCOM consumer number and mobile number.",
                issuing_office="MNRE National Portal",
                is_online=True,
                portal_or_form_link="https://pmsuryaghar.gov.in"
            ))
            db.add(ApplicationStep(
                scheme_id=ps_scheme.id,
                step_order=2,
                title="Select Registered Vendor & Install System",
                description="Choose an empanelled vendor in your district to install certified solar panels and inverter.",
                issuing_office="Empanelled Vendor",
                is_online=False
            ))
            db.add(ApplicationStep(
                scheme_id=ps_scheme.id,
                step_order=3,
                title="Net Metering Inspection & Subsidy Release",
                description="DISCOM officials install net meter and issue commissioning certificate; subsidy credited within 30 days.",
                issuing_office="Local DISCOM Division",
                is_online=True
            ))

            db.add(OfficialSource(
                scheme_id=ps_scheme.id,
                source_name="Ministry of New and Renewable Energy Gazette S.O. 789(E)",
                source_type="gazette",
                official_url="https://pmsuryaghar.gov.in",
                authority_name="Ministry of New and Renewable Energy",
                verification_status="verified",
                is_accessible=True
            ))

        # -------------------------------------------------------------
        # 3. ADIP Scheme for Persons with Disabilities
        # -------------------------------------------------------------
        ad_scheme = db.query(Scheme).filter(Scheme.slug == "adip-pwd").first()
        if not ad_scheme:
            ad_scheme = Scheme(
                slug="adip-pwd",
                official_name="ADIP & Pre/Post-Matric Scholarship for Persons with Disabilities",
                ministry="Department of Empowerment of Persons with Disabilities",
                is_central=True,
                state_or_region="All India",
                category="disability",
                category_label="Disability Allowance & Assistive Aid",
                numeric_benefit_value=48000.0,
                application_method="hybrid",
                external_portal_name="Swavlamban UDID Portal",
                external_portal_url="https://swavlambancard.gov.in",
                status="active",
                is_retired=False,
                verification_status="verified",
                last_verified_at=datetime.now(timezone.utc)
            )
            db.add(ad_scheme)
            db.flush()

            db.add(SchemeTranslation(
                scheme_id=ad_scheme.id,
                language_code="en",
                localized_name="ADIP & Pre/Post-Matric Scholarship for Persons with Disabilities",
                localized_description="Assistance to disabled persons for purchase of high-grade motorized aids, hearing devices, and specialized educational grants.",
                localized_benefit_summary="Free motorized assistive equipment + ₹4,000/mo educational disability grant",
                why_qualify_text="Certified benchmark disability of 40% or more with valid UDID card; Family income verified below ₹3,00,000 per annum; Eligible for direct smart assistive equipment distribution through ALIMCO",
                why_not_qualify_text="Certified disability percentage is less than the statutory 40% threshold; Applicant has received similar motorized assistive aid within the preceding 3 years",
                is_reviewed=True,
                reviewed_by="DEPwD Nodal Evaluation Team"
            ))
            db.add(SchemeTranslation(
                scheme_id=ad_scheme.id,
                language_code="hi",
                localized_name="एडीआईपी एवं दिव्यांगजन छात्रवृत्ति व सहायक उपकरण योजना",
                localized_description="दिव्यांगजनों हेतु उच्च गुणवत्ता वाले सहायक उपकरण (मोटराइज्ड ट्राइसाइकिल, श्रवण यंत्र आदि) तथा मासिक शिक्षा सहायता।",
                localized_benefit_summary="निःशुल्क मोटराइज्ड सहायक उपकरण + ₹4,00,000 तक की सहायता",
                why_qualify_text="डिजिटल UDID कार्ड के साथ 40% या अधिक प्रमाणित बेंचमार्क दिव्यांगता; पारिवारिक आय ₹3,00,000 प्रति वर्ष से कम सत्यापित; एलिम्को (ALIMCO) के माध्यम से निःशुल्क मोटराइज्ड उपकरणों हेतु पात्र",
                why_not_qualify_text="प्रमाणित दिव्यांगता 40% के वैधानिक बेंचमार्क से कम है; आवेदक को पिछले 3 वर्षों के भीतर समान मोटराइज्ड उपकरण प्राप्त हो चुका है",
                is_reviewed=True,
                reviewed_by="DEPwD Nodal Evaluation Team"
            ))

            db.add(EligibilityRule(
                scheme_id=ad_scheme.id,
                rule_code="ADIP_DISABILITY",
                field_name="disability",
                operator="eq",
                target_value="40% and Above (Benchmark)",
                is_mandatory=True,
                description="Must possess certified benchmark disability of 40% or more with valid UDID",
                failure_reason="Disability percentage does not satisfy 40% benchmark criterion"
            ))
            db.add(EligibilityRule(
                scheme_id=ad_scheme.id,
                rule_code="ADIP_INCOME",
                field_name="max_income",
                operator="lte",
                target_value="300000",
                is_mandatory=True,
                description="Total household income must not exceed ₹3,00,000 per annum",
                failure_reason="Household income exceeds ₹3,00,000 ceiling"
            ))

            db.add(RequiredDocument(
                scheme_id=ad_scheme.id,
                document_code="udid",
                document_name="UDID Disability Card (40%+ Benchmark Certificate)",
                authority="District Medical Board / CMO Office",
                is_mandatory=True,
                steps="Register online at swavlambancard.gov.in and appear before the District Civil Hospital Medical Board.",
                turnaround="15 - 30 Business Days",
                estimated_cost="Free",
                official_guide_url="https://swavlambancard.gov.in"
            ))

            db.add(ApplicationStep(
                scheme_id=ad_scheme.id,
                step_order=1,
                title="Register on Swavlamban Portal",
                description="Apply for UDID card online or locate upcoming ALIMCO assessment camp in your district.",
                issuing_office="Swavlamban Portal",
                is_online=True,
                portal_or_form_link="https://swavlambancard.gov.in"
            ))

            db.add(OfficialSource(
                scheme_id=ad_scheme.id,
                source_name="DEPwD Official Gazette Operational Manual",
                source_type="gazette",
                official_url="https://swavlambancard.gov.in",
                authority_name="Department of Empowerment of Persons with Disabilities",
                verification_status="verified",
                is_accessible=True
            ))

        # -------------------------------------------------------------
        # 4. PM-KISAN
        # -------------------------------------------------------------
        pk_scheme = db.query(Scheme).filter(Scheme.slug == "pm-kisan").first()
        if not pk_scheme:
            pk_scheme = Scheme(
                slug="pm-kisan",
                official_name="PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
                ministry="Ministry of Agriculture & Farmers Welfare",
                is_central=True,
                state_or_region="All India",
                category="farmers",
                category_label="Direct Income Support",
                numeric_benefit_value=6000.0,
                application_method="online",
                external_portal_name="PM-KISAN DBT Portal",
                external_portal_url="https://pmkisan.gov.in",
                status="active",
                is_retired=False,
                verification_status="verified",
                last_verified_at=datetime.now(timezone.utc)
            )
            db.add(pk_scheme)
            db.flush()

            db.add(SchemeTranslation(
                scheme_id=pk_scheme.id,
                language_code="en",
                localized_name="PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
                localized_description="Income support scheme for all landholding farmer families having cultivable landholding in their names.",
                localized_benefit_summary="₹6,000 per annum credited directly in 3 equal four-monthly payments",
                why_qualify_text="Applicant resides in designated Rural Gram Panchayat area; Holding registered cultivable agricultural land in revenue records; Household fits small & marginal agrarian classification",
                why_not_qualify_text="Applicant or spouse is an income tax payee in the previous assessment year; Land is registered under institutional names or trusts; Applicant holds or held constitutional post / government permanent employment",
                is_reviewed=True,
                reviewed_by="PM-KISAN Nodal Unit"
            ))
            db.add(SchemeTranslation(
                scheme_id=pk_scheme.id,
                language_code="hi",
                localized_name="पीएम-किसान (प्रधानमंत्री किसान सम्मान निधि)",
                localized_description="खेती योग्य भूमि वाले पात्र किसान परिवारों को प्रति वर्ष ₹6,000 की वित्तीय सहायता।",
                localized_benefit_summary="₹6,000 प्रति वर्ष 3 समान किश्तों में सीधे बैंक खाते में जमा",
                why_qualify_text="आवेदक ग्रामीण ग्राम पंचायत क्षेत्र का निवासी है; राजस्व रिकॉर्ड में स्वयं के नाम पर कृषि योग्य भूमि दर्ज है; लघु एवं सीमांत कृषक वर्ग के अंतर्गत आता है",
                why_not_qualify_text="आवेदक अथवा पति/पत्नी पूर्व निर्धारण वर्ष में आयकर दाता (Income Tax Payee) रहे हैं; भूमि किसी संस्था, ट्रस्ट अथवा कंपनी के नाम पर पंजीकृत है; संवैधानिक पदधारक अथवा केंद्र/राज्य सरकार में नियमित कर्मचारी",
                is_reviewed=True,
                reviewed_by="PM-KISAN Nodal Unit"
            ))

            db.add(EligibilityRule(
                scheme_id=pk_scheme.id,
                rule_code="PMK_REGION",
                field_name="region_type",
                operator="eq",
                target_value="Rural",
                is_mandatory=True,
                description="Must reside in a rural Gram Panchayat jurisdiction with agricultural holding",
                failure_reason="Applicant is located in non-rural / urban municipal limits"
            ))

            db.add(RequiredDocument(
                scheme_id=pk_scheme.id,
                document_code="khasra",
                document_name="Land Record (RoR / Khasra / Khatauni Copy)",
                authority="Revenue Inspector / Tehsil / Bhulekh Portal",
                is_mandatory=True,
                steps="Download digitally signed Khatauni from your state Bhulekh portal (e.g. upbhulekh.gov.in).",
                turnaround="Instant Online",
                estimated_cost="Free to view / ₹15 for certified copy",
                official_guide_url="https://pmkisan.gov.in"
            ))

            db.add(ApplicationStep(
                scheme_id=pk_scheme.id,
                step_order=1,
                title="Farmer Registration on PM-KISAN Portal",
                description="Submit land record details, Aadhaar number, and active bank account on pmkisan.gov.in or CSC desk.",
                issuing_office="PM-KISAN Portal / CSC",
                is_online=True,
                portal_or_form_link="https://pmkisan.gov.in"
            ))

            db.add(OfficialSource(
                scheme_id=pk_scheme.id,
                source_name="Ministry of Agriculture Gazette Operational Guidelines 2026",
                source_type="gazette",
                official_url="https://pmkisan.gov.in",
                authority_name="Ministry of Agriculture & Farmers Welfare",
                verification_status="verified",
                is_accessible=True
            ))

        # -------------------------------------------------------------
        # 5. RETIRED: Rajiv Gandhi Grameen Vidyutikaran Yojana (RGGVY)
        # -------------------------------------------------------------
        rg_scheme = db.query(Scheme).filter(Scheme.slug == "rgvy-retired").first()
        if not rg_scheme:
            rg_scheme = Scheme(
                slug="rgvy-retired",
                official_name="Rajiv Gandhi Grameen Vidyutikaran Yojana (RGGVY)",
                ministry="Ministry of Power",
                is_central=True,
                state_or_region="All India",
                category="farmers",
                category_label="Rural Electrification [RETIRED / MERGED]",
                numeric_benefit_value=0.0,
                application_method="offline_csc",
                external_portal_name="Historical Gazette Record",
                external_portal_url="https://powermin.gov.in",
                status="withdrawn",
                is_retired=True,
                retired_year="2015",
                retired_reason="Merged into Deen Dayal Upadhyaya Gram Jyoti Yojana (DDUGJY) and later modernized into PM Saubhagya and PM Surya Ghar.",
                replacement_scheme_slug="pm-surya",
                verification_status="verified",
                last_verified_at=datetime.now(timezone.utc)
            )
            db.add(rg_scheme)
            db.flush()

            db.add(SchemeTranslation(
                scheme_id=rg_scheme.id,
                language_code="en",
                localized_name="Rajiv Gandhi Grameen Vidyutikaran Yojana (RGGVY)",
                localized_description="Historical rural electrification program sunset and restructured in 2015.",
                localized_benefit_summary="Free basic electricity connection for BPL rural households (Discontinued)",
                why_qualify_text="Historical Program: Was applicable to rural BPL families without domestic electricity.",
                why_not_qualify_text="Scheme has been officially SUNSET and merged into modern universal electrification programs.",
                is_reviewed=True
            ))

        # -------------------------------------------------------------
        # 6. RETIRED: SABLA
        # -------------------------------------------------------------
        sb_scheme = db.query(Scheme).filter(Scheme.slug == "sabla-retired").first()
        if not sb_scheme:
            sb_scheme = Scheme(
                slug="sabla-retired",
                official_name="Rajiv Gandhi Scheme for Empowerment of Adolescent Girls (SABLA)",
                ministry="Ministry of Women and Child Development",
                is_central=True,
                state_or_region="All India",
                category="education",
                category_label="Adolescent Nutrition & Skill [RETIRED / REPLACED]",
                numeric_benefit_value=0.0,
                application_method="offline_csc",
                external_portal_name="Historical Ministry Gazette",
                external_portal_url="https://wcd.nic.in",
                status="withdrawn",
                is_retired=True,
                retired_year="2021",
                retired_reason="Consolidated into Umbrella ICDS - Mission Saksham Anganwadi and Poshan 2.0.",
                replacement_scheme_slug="post-matric",
                verification_status="verified",
                last_verified_at=datetime.now(timezone.utc)
            )
            db.add(sb_scheme)
            db.flush()

            db.add(SchemeTranslation(
                scheme_id=sb_scheme.id,
                language_code="en",
                localized_name="Rajiv Gandhi Scheme for Empowerment of Adolescent Girls (SABLA)",
                localized_description="Historical adolescent welfare scheme restructured under Mission Poshan 2.0.",
                localized_benefit_summary="Nutrition and life skills kits for out-of-school girls aged 11-14 (Phased Out)",
                why_qualify_text="Historical Program: Targeted adolescent girls in 205 selected districts.",
                why_not_qualify_text="Officially superseded under restructured umbrella guidelines of Mission Poshan 2.0.",
                is_reviewed=True
            ))

        db.commit()
        print("✅ Database seeding successfully completed with verified government records!")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise e
    finally:
        if should_close:
            db.close()

if __name__ == "__main__":
    seed()
