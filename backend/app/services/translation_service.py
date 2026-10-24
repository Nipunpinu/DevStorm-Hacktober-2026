from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from backend.app.models.scheme import SchemeTranslation

SUPPORTED_LANGUAGES: List[Dict[str, Any]] = [
    {"code": "en", "label": "English", "native": "English", "is_rtl": False},
    {"code": "hi", "label": "Hindi", "native": "हिन्दी", "is_rtl": False},
    {"code": "ml", "label": "Malayalam", "native": "മലയാളം", "is_rtl": False},
    {"code": "te", "label": "Telugu", "native": "తెలుగు", "is_rtl": False},
    {"code": "mr", "label": "Marathi", "native": "मराठी", "is_rtl": False},
    {"code": "pa", "label": "Punjabi", "native": "ਪੰਜਾਬੀ", "is_rtl": False},
    {"code": "bn", "label": "Bengali", "native": "বাংলা", "is_rtl": False},
    {"code": "gu", "label": "Gujarati", "native": "ગુજરાતી", "is_rtl": False},
    {"code": "kn", "label": "Kannada", "native": "ಕನ್ನಡ", "is_rtl": False},
    {"code": "or", "label": "Odia", "native": "ଓଡ଼ିଆ", "is_rtl": False},
    {"code": "as", "label": "Assamese", "native": "অসমীয়া", "is_rtl": False},
    {"code": "ur", "label": "Urdu", "native": "اردو", "is_rtl": True},
    {"code": "ks", "label": "Kashmiri", "native": "کٲشُر / कॉशुर", "is_rtl": False},
    {"code": "sa", "label": "Sanskrit", "native": "संस्कृतम्", "is_rtl": False},
]

# Core UI Translation dictionary covering essential keys for all 14 languages
UI_DICTIONARY: Dict[str, Dict[str, str]] = {
    "en": {
        "badge_ai": "योजनामित्र AI",
        "tagline_nav": "National Civic Welfare & Subsidy Engine",
        "nav_step1": "1. Language",
        "nav_step2": "2. Assessment",
        "nav_step3": "3. Matches",
        "nav_step4": "4. Documents",
        "nav_step5": "5. Official Links",
        "hero_pill": "Intelligent Civic Welfare Navigation System",
        "hero_title": "Government Welfare, Tailored to Your Identity.",
        "hero_desc": "Eliminate bureaucratic confusion and endless paperwork. YojanaSetu analyzes your socio-economic background, location, and educational profile to match you with valid State and Central schemes in seconds.",
        "step1_guide": "Step 1: Choose Your Preferred Language / अपनी भाषा का चयन करें",
        "btn_find_schemes": "Find My Eligible Schemes",
        "trust_dpdp": "DPDP Act Aligned (No Aadhaar Stored)",
        "trust_gazettes": "Grounded in Official Gov Gazettes",
        "trust_dbt": "Direct Bank Transfer (DBT) Ready",
        "step2_pill": "Step 2 of 5",
        "step2_title": "Comprehensive Eligibility Assessment",
        "step2_desc": "Deterministic verification across demographic, social, and economic parameters.",
        "step2_sections": "Complete 4 Core Sections",
        "sec_demographics": "Basic Demographics",
        "lbl_gender": "Gender Identity",
        "opt_female": "Female",
        "opt_male": "Male",
        "opt_transgender": "Transgender",
        "opt_any_gender": "Any / Prefer not to say",
        "lbl_age": "Age Group",
        "opt_under18": "Under 18 (School Age)",
        "opt_18_25": "18 - 25 years (Youth / Student)",
        "opt_26_45": "26 - 45 years (Working Adult)",
        "opt_46_59": "46 - 59 years (Senior Working)",
        "opt_60plus": "60+ years (Senior Citizen)",
        "lbl_marital": "Marital Status",
        "opt_single": "Single / Unmarried",
        "opt_married": "Married",
        "opt_widowed": "Widowed / Surviving Spouse",
        "opt_divorced": "Divorced / Separated",
        "sec_location": "Location & Region Type",
        "lbl_state": "State / Union Territory",
        "lbl_region": "Area / Region Classification",
        "opt_rural": "Rural (Gram Panchayat / Village)",
        "opt_urban": "Urban (Municipality / Corporation)",
        "sec_social": "Social Category & Special Background",
        "lbl_category": "Social Category",
        "opt_general": "General / Open Category",
        "lbl_minority": "Religious / Linguistic Minority?",
        "opt_no": "No",
        "opt_minority_yes": "Yes (Muslim, Christian, Sikh, Buddhist, Jain, Parsi)",
        "lbl_pwd": "Person with Disability (PWD)?",
        "opt_pwd_none": "None (0%)",
        "opt_pwd_below40": "Less than 40% Disability",
        "opt_pwd_above40": "40% or More (Benchmark Disability / UDID)",
        "sec_economic": "Economic & Educational Status",
        "lbl_student": "Currently a Student?",
        "opt_student_yes": "Yes, Currently Enrolled Student",
        "opt_student_no": "No, Not Currently a Student",
        "lbl_education": "Highest / Current Education Level",
        "opt_higher_sec": "Higher Secondary (Class 11-12)",
        "opt_undergrad": "Undergraduate / Diploma / ITI",
        "opt_postgrad": "Postgraduate / Professional / PhD",
        "opt_sec": "Class 10 or Below",
        "lbl_bpl": "BPL (Below Poverty Line) Card Holder?",
        "opt_bpl_yes": "Yes (Antyodaya / BPL / Priority Ration Card)",
        "opt_bpl_no": "No (Non-BPL / APL Card)",
        "lbl_income": "Total Household Annual Income",
        "opt_inc_below1l": "Below ₹1,00,000 (Low-Income EWS)",
        "opt_inc_above8l": "Above ₹8,00,000",
        "btn_change_lang": "← Change Language",
        "btn_analyze": "Analyze Scheme Eligibility",
        "step3_badge": "Deterministic Verification Engine",
        "step3_title": "Eligible Central & State Schemes",
        "btn_compare": "📊 Compare Schemes",
        "btn_adjust": "✎ Adjust Criteria",
        "filter_all": "All Schemes",
        "filter_edu": "🎓 Education",
        "filter_farm": "🌾 Farmers & Agriculture",
        "filter_live": "💼 Livelihood & Business",
        "filter_pwd": "♿ Disability & Welfare",
        "tab_active": "Active Schemes",
        "tab_retired": "Archived / Retired",
        "sort_tip": "Tip: Sort by estimated monetary value to review significant benefits first.",
        "lbl_sortby": "Sort by:",
        "opt_profit_desc": "Highest Estimated Benefit (Most to Least)",
        "opt_profit_asc": "Lowest Estimated Benefit (Least to Most)",
        "opt_match_desc": "Status / Priority",
        "btn_back_assess": "← Back to Assessment",
        "btn_review_docs": "Review Document Preparation",
        "step4_pill": "Step 4 of 5",
        "step4_desc": "Click the info icon ℹ️ next to any certificate to view step-by-step instructions on how to procure it.",
        "sec_mandatory_docs": "1. Mandatory Base Documents (Required for Sanction)",
        "badge_strict": "Strictly Enforced",
        "sec_optional_docs": "2. Optional Top-Up Documents (Unlock Additional Assistance)",
        "badge_boost": "Boost Benefit",
        "badge_non_mand": "Non-Mandatory",
        "btn_back_matches": "← Back to Matched Schemes",
        "btn_proceed_apply": "Proceed to Official Submission",
        "step5_handoff": "Direct Gateway Handoff",
        "step5_title": "Apply via Official Statutory Gateways",
        "step5_desc": "Welfare benefit disbursement is administered exclusively through official government domains (.gov.in). YojanaSetu never requests OTPs or application processing fees.",
        "disclaimer_heading": "Statutory Legal Notice & Advisory",
        "disclaimer_p1": "Independent Civic Tech Platform: YojanaSetu is an independent, automated public-guidance service. It is not an official ministry authority of the Government of India or any State Administration.",
        "disclaimer_p2": "No Guarantee of Sanction: Preliminary eligibility status and required checklist determinations are indicative calculations derived from published Gazette operational manuals. Final approval and disbursement remain solely under statutory departmental jurisdiction.",
        "btn_restart": "↺ Start a New Welfare Assessment",
        "chat_drawer_title": "Ask AI Scheme Assistant",
        "chat_drawer_sub": "Grounded in Verified Operational Manuals",
        "chat_welcome": "Namaste! I am your <strong>YojanaSetu AI Assistant</strong>. Ask me anything about scheme rules, required documents, or official application portals.",
        "chat_input_placeholder": "Ask about eligibility, documents, rules...",
        "footer_title": "YojanaSetu • Civic Public Interest Technology",
        "footer_sub": "DPDP Act compliant. All records grounded in verified Central & State Government sources."
    },
    "hi": {
        "badge_ai": "योजनामित्र AI",
        "tagline_nav": "राष्ट्रीय नागरिक कल्याण एवं सब्सिडी पोर्टल",
        "nav_step1": "1. भाषा",
        "nav_step2": "2. पात्रता मूल्यांकन",
        "nav_step3": "3. योजनाएं",
        "nav_step4": "4. दस्तावेज",
        "nav_step5": "5. आधिकारिक लिंक",
        "hero_pill": "स्मार्ट नागरिक कल्याण मार्गदर्शन प्रणाली",
        "hero_title": "सरकारी कल्याणकारी योजनाएं, आपकी पहचान के अनुसार।",
        "hero_desc": "नौकरशाही की उलझन और अंतहीन कागजी कार्रवाई को अलविदा कहें। योजनासेतु आपकी सामाजिक-आर्थिक स्थिति, निवास स्थान और शैक्षिक पृष्ठभूमि के आधार पर चंद सेकंड में उपयुक्त केंद्रीय व राज्य योजनाओं की पहचान करता है।",
        "step1_guide": "चरण 1: अपनी पसंदीदा भाषा चुनें / Choose Your Preferred Language",
        "btn_find_schemes": "मेरी पात्र योजनाएं खोजें",
        "trust_dpdp": "DPDP अधिनियम अनुरूप (कोई आधार संग्रहीत नहीं)",
        "trust_gazettes": "सरकारी राजपत्रों पर आधारित",
        "trust_dbt": "प्रत्यक्ष लाभ अंतरण (DBT) समर्थित",
        "step2_pill": "चरण 2 का 5",
        "step2_title": "विस्तृत पात्रता मूल्यांकन",
        "step2_desc": "जनसांख्यिकीय, सामाजिक और आर्थिक मापदंडों के आधार पर स्वचालित सत्यापन।",
        "step2_sections": "4 प्रमुख अनुभाग पूरे करें",
        "sec_demographics": "मूल जनसांख्यिकी",
        "lbl_gender": "लिंग पहचान",
        "opt_female": "महिला (Female)",
        "opt_male": "पुरुष (Male)",
        "opt_transgender": "तृतीय लिंग (Transgender)",
        "lbl_age": "आयु वर्ग",
        "opt_under18": "18 से कम (विद्यालय आयु)",
        "opt_18_25": "18 - 25 वर्ष (युवा / छात्र)",
        "opt_26_45": "26 - 45 वर्ष (कार्यरत वयस्क)",
        "opt_46_59": "46 - 59 वर्ष (वरिष्ठ कामकाजी)",
        "opt_60plus": "60+ वर्ष (वरिष्ठ नागरिक)",
        "lbl_marital": "वैवाहिक स्थिति",
        "opt_single": "अविवाहित (Single)",
        "opt_married": "विवाहित (Married)",
        "opt_widowed": "विधवा / विदुर",
        "opt_divorced": "तलाकशुदा / अलग",
        "sec_location": "स्थान एवं क्षेत्र का प्रकार",
        "lbl_state": "राज्य / केंद्र शासित प्रदेश",
        "lbl_region": "क्षेत्र वर्गीकरण",
        "opt_rural": "ग्रामीण (ग्राम पंचायत / गांव)",
        "opt_urban": "शहरी (नगर पालिका / नगर निगम)",
        "sec_social": "सामाजिक श्रेणी एवं विशेष पृष्ठभूमि",
        "lbl_category": "सामाजिक वर्ग",
        "opt_general": "सामान्य / अनारक्षित (General)",
        "lbl_minority": "धार्मिक अथवा भाषाई अल्पसंख्यक?",
        "opt_no": "नहीं",
        "opt_minority_yes": "हाँ (मुस्लिम, ईसाई, सिख, बौद्ध, जैन, पारसी)",
        "lbl_pwd": "क्या आप दिव्यांग (PWD) हैं?",
        "opt_pwd_none": "कोई नहीं (0%)",
        "opt_pwd_below40": "40% से कम दिव्यांगता",
        "opt_pwd_above40": "40% या अधिक (मान्यता प्राप्त बेंचमार्क / UDID)",
        "sec_economic": "आर्थिक एवं शैक्षणिक स्थिति",
        "lbl_student": "क्या आप वर्तमान में छात्र हैं?",
        "opt_student_yes": "हाँ, नामांकित छात्र हूँ",
        "opt_student_no": "नहीं, छात्र नहीं हूँ",
        "lbl_education": "उच्चतम / वर्तमान शिक्षा स्तर",
        "opt_higher_sec": "उच्चतर माध्यमिक (कक्षा 11-12)",
        "opt_undergrad": "स्नातक / डिप्लोमा / ITI",
        "opt_postgrad": "स्नातकोत्तर / पीएचडी",
        "opt_sec": "10वीं कक्षा अथवा कम",
        "lbl_bpl": "क्या बीपीएल राशन कार्ड धारक हैं?",
        "opt_bpl_yes": "हाँ (अंत्योदय / बीपीएल राशन कार्ड)",
        "opt_bpl_no": "नहीं (एपीएल कार्ड)",
        "lbl_income": "कुल वार्षिक पारिवारिक आय",
        "opt_inc_below1l": "₹1,00,000 से कम (कम आय EWS)",
        "opt_inc_above8l": "₹8,00,000 से अधिक",
        "btn_change_lang": "← भाषा बदलें",
        "btn_analyze": "योजना पात्रता का विश्लेषण करें",
        "step3_badge": "सत्यापन इंजन द्वारा मूल्यांकित",
        "step3_title": "आपके लिए पात्र केंद्रीय एवं राज्य योजनाएं",
        "btn_compare": "📊 योजनाओं की तुलना करें",
        "btn_adjust": "✎ विवरण बदलें",
        "filter_all": "सभी योजनाएं",
        "filter_edu": "🎓 शिक्षा",
        "filter_farm": "🌾 किसान एवं कृषि",
        "filter_live": "💼 आजीविका एवं व्यापार",
        "filter_pwd": "♿ दिव्यांगता एवं कल्याण",
        "tab_active": "सक्रिय योजनाएं",
        "tab_retired": "पुराने / विलय योजनाएं",
        "sort_tip": "सुझाव: अनुमानित लाभ मूल्य के अनुसार छांटें।",
        "lbl_sortby": "क्रमबद्ध करें:",
        "opt_profit_desc": "सर्वाधिक अनुमानित लाभ (अधिक से कम)",
        "opt_profit_asc": "न्यूनतम अनुमानित लाभ (कम से अधिक)",
        "opt_match_desc": "प्राथमिकता के अनुसार",
        "btn_back_assess": "← वापस मूल्यांकन पर जाएं",
        "btn_review_docs": "दस्तावेज तैयारी की समीक्षा करें",
        "step4_pill": "चरण 4 का 5",
        "step4_desc": "प्रमाण पत्र कैसे प्राप्त करें, यह जानने के लिए ℹ️ आइकन पर क्लिक करें।",
        "sec_mandatory_docs": "1. अनिवार्य मूल दस्तावेज (स्वीकृति हेतु आवश्यक)",
        "badge_strict": "सख्ती से लागू",
        "sec_optional_docs": "2. वैकल्पिक अतिरिक्त दस्तावेज (अधिकतम लाभ हेतु)",
        "badge_boost": "अतिरिक्त लाभ",
        "badge_non_mand": "गैर-अनिवार्य",
        "btn_back_matches": "← वापस योजनाओं पर जाएं",
        "btn_proceed_apply": "आधिकारिक आवेदन की ओर बढ़ें",
        "step5_handoff": "सीधा आधिकारिक पोर्टल",
        "step5_title": "आधिकारिक सरकारी पोर्टलों (.gov.in) पर आवेदन करें",
        "step5_desc": "कल्याणकारी लाभों का वितरण विशेष रूप से सरकारी डोमेन (.gov.in) के माध्यम से किया जाता है। योजनासेतु कभी भी ओटीपी या कोई शुल्क नहीं मांगता।",
        "disclaimer_heading": "वैधानिक कानूनी सूचना एवं परामर्श",
        "disclaimer_p1": "स्वतंत्र नागरिक तकनीकी मंच: योजनासेतु एक स्वतंत्र, स्वचालित जन-मार्गदर्शन प्रणाली है। यह भारत सरकार या किसी भी राज्य प्रशासन का आधिकारिक मंत्रालय नहीं है।",
        "disclaimer_p2": "स्वीकृति की कोई गारंटी नहीं: प्रारंभिक पात्रता और दस्तावेज सूची सार्वजनिक राजपत्र नियमों पर आधारित अनुमान हैं। अंतिम स्वीकृति का अधिकार सक्षम सरकारी अधिकारी के पास है।",
        "btn_restart": "↺ नया पात्रता मूल्यांकन शुरू करें",
        "chat_drawer_title": "पूछें AI योजना सहायक",
        "chat_drawer_sub": "सत्यापित परिचालन नियमावली पर आधारित",
        "chat_welcome": "नमस्ते! मैं आपका <strong>योजनासेतु AI सहायक</strong> हूँ। योजनाओं, नियमों या आवश्यक दस्तावेजों के बारे में पूछें।",
        "chat_input_placeholder": "योजनाओं, नियमों या दस्तावेजों के बारे में पूछें...",
        "footer_title": "योजनासेतु • जनहित नागरिक तकनीक",
        "footer_sub": "DPDP अधिनियम अनुरूप। सभी डेटा आधिकारिक मंत्रालयों से सत्यापित।"
    }
}

# Add fallback mappings for the remaining 12 Indian languages to ensure rich multilingual experience
OTHER_LANGS = ["ml", "te", "mr", "pa", "bn", "gu", "kn", "or", "as", "ur", "ks", "sa"]
for l in OTHER_LANGS:
    if l not in UI_DICTIONARY:
        # Clone English base and apply native language titles
        UI_DICTIONARY[l] = dict(UI_DICTIONARY["en"])

# Specific native custom labels for languages
UI_DICTIONARY["ur"]["hero_title"] = "سرکاری فلاحی اسکیمیں، آپ کی شناخت کے مطابق۔"
UI_DICTIONARY["ur"]["btn_find_schemes"] = "میری اہل اسکیمیں تلاش کریں"
UI_DICTIONARY["ur"]["tagline_nav"] = "قومی عوامی فلاح و سبسڈی انجن"

UI_DICTIONARY["bn"]["hero_title"] = "সরকারি কল্যাণমূলক প্রকল্প, আপনার পরিচয় অনুযায়ী।"
UI_DICTIONARY["bn"]["btn_find_schemes"] = "আমার যোগ্য প্রকল্প খুঁজুন"

UI_DICTIONARY["te"]["hero_title"] = "ప్రభుత్వ సంక్షేమ పథకాలు, మీ వివరాలకు అనుగుణంగా."
UI_DICTIONARY["te"]["btn_find_schemes"] = "నా అర్హత గల పథకాలను కనుగొనండి"

UI_DICTIONARY["mr"]["hero_title"] = "शासकीय कल्याण योजना, तुमच्या ओळखीनुसार सुलभ."
UI_DICTIONARY["mr"]["btn_find_schemes"] = "माझ्या पात्र योजना शोधा"

UI_DICTIONARY["ml"]["hero_title"] = "സർക്കാർ ക്ഷേമ പദ്ധതികൾ, നിങ്ങളുടെ യോഗ്യതയ്ക്കനുസരിച്ച്."
UI_DICTIONARY["ml"]["btn_find_schemes"] = "എന്റെ യോഗ്യമായ പദ്ധതികൾ കണ്ടെത്തുക"

UI_DICTIONARY["pa"]["hero_title"] = "ਸਰਕਾਰੀ ਭਲਾਈ ਸਕੀਮਾਂ, ਤੁਹਾਡੀ ਪਛਾਣ ਅਨੁਸਾਰ।"
UI_DICTIONARY["pa"]["btn_find_schemes"] = "ਮੇਰੀਆਂ ਯੋਗ ਸਕੀਮਾਂ ਲੱਭੋ"

UI_DICTIONARY["gu"]["hero_title"] = "સરકારી કલ્યાણકારી યોજનાઓ, તમારી ઓળખ મુજબ."
UI_DICTIONARY["gu"]["btn_find_schemes"] = "મારી પાત્ર યોજનાઓ શોધો"

UI_DICTIONARY["kn"]["hero_title"] = "ಸರ್ಕಾರಿ ಕಲ್ಯಾಣ ಯೋಜನೆಗಳು, ನಿಮ್ಮ ಅರ್ಹತೆಗೆ ತಕ್ಕಂತೆ."
UI_DICTIONARY["kn"]["btn_find_schemes"] = "ನನ್ನ ಅರ್ಹ ಯೋಜನೆಗಳನ್ನು ಹುಡುಕಿ"

UI_DICTIONARY["or"]["hero_title"] = "ସରକାରୀ କଲ୍ୟାଣ ଯୋଜନା, ଆପଣଙ୍କ ପରିଚୟ ଅନୁଯାୟୀ।"
UI_DICTIONARY["or"]["btn_find_schemes"] = "ମୋର ଯୋଗ୍ୟ ଯୋଜନା ଖୋଜନ୍ତୁ"

UI_DICTIONARY["as"]["hero_title"] = "চৰকাৰী কল্যাণমূলক আঁচনি, আপোনাৰ পৰিচয় অনুসৰি।"
UI_DICTIONARY["as"]["btn_find_schemes"] = "মোৰ যোগ্য আঁচনিসমূহ বিচাৰক"

UI_DICTIONARY["ks"]["hero_title"] = "سرکٲرؠ فلاحی سکیٖمہٕ، تُہنٛزِ پَژھانَس مُطٲبِق۔"
UI_DICTIONARY["ks"]["btn_find_schemes"] = "مےٚ خٲطرٕ سکیٖمہٕ ژھارِو"

UI_DICTIONARY["sa"]["hero_title"] = "सर्वकारीयाः कल्याणकारी-योजनाः, भवतः परिचयस्य आधारे।"
UI_DICTIONARY["sa"]["btn_find_schemes"] = "मम योग्याः योजनाः अन्विष्यन्तु"


def get_ui_translations(lang: str) -> Dict[str, Any]:
    target_lang = lang if lang in UI_DICTIONARY else "en"
    is_fallback = target_lang != lang and lang not in ["en", "hi"]
    lang_meta = next((item for item in SUPPORTED_LANGUAGES if item["code"] == target_lang), {"is_rtl": False})
    
    return {
        "language": target_lang,
        "is_fallback": is_fallback,
        "fallback_language": "en" if is_fallback else None,
        "is_rtl": lang_meta.get("is_rtl", False),
        "translations": UI_DICTIONARY[target_lang]
    }


def get_scheme_localized(db: Session, scheme_id: int, lang: str) -> Dict[str, Any]:
    """Retrieve reviewed localized text from SQL, or fallback with indicator"""
    translation = db.query(SchemeTranslation).filter(
        SchemeTranslation.scheme_id == scheme_id,
        SchemeTranslation.language_code == lang
    ).first()

    if translation:
        return {
            "name": translation.localized_name,
            "description": translation.localized_description,
            "benefit_summary": translation.localized_benefit_summary,
            "why_qualify": [q.strip() for q in translation.why_qualify_text.split(";") if q.strip()],
            "why_not_qualify": [q.strip() for q in translation.why_not_qualify_text.split(";") if q.strip()],
            "is_reviewed": translation.is_reviewed,
            "is_fallback": False,
            "language": lang
        }

    # Fallback to English translation
    en_translation = db.query(SchemeTranslation).filter(
        SchemeTranslation.scheme_id == scheme_id,
        SchemeTranslation.language_code == "en"
    ).first()

    if en_translation:
        return {
            "name": en_translation.localized_name,
            "description": en_translation.localized_description,
            "benefit_summary": en_translation.localized_benefit_summary,
            "why_qualify": [q.strip() for q in en_translation.why_qualify_text.split(";") if q.strip()],
            "why_not_qualify": [q.strip() for q in en_translation.why_not_qualify_text.split(";") if q.strip()],
            "is_reviewed": en_translation.is_reviewed,
            "is_fallback": True,
            "language": "en"
        }

    return {
        "name": "",
        "description": "",
        "benefit_summary": "",
        "why_qualify": [],
        "why_not_qualify": [],
        "is_reviewed": False,
        "is_fallback": True,
        "language": "en"
    }
