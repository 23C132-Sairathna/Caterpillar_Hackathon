import streamlit as st
import pymongo
from datetime import datetime

st.set_page_config(page_title="Operator Training Hub", layout="wide")

with st.sidebar:
    if st.button("Logout"):
        st.session_state.clear()
        st.switch_page("Login.py")
        
if "role" not in st.session_state:
    st.warning("Please login to access this page.")
    st.stop()

MONGO_URI = "mongodb+srv://nshabnam2006:1pZuRuArGzbbNFOm@cluster0.oik5ct5.mongodb.net/?retryWrites=true&w=majority"
client = pymongo.MongoClient(MONGO_URI)
db = client["cat_operator_assistant"]
incident_collection = db["incident_logs"]


latest_log = incident_collection.find_one(
    {"Fuel Used (L)": {"$exists": True}},
    sort=[("timestamp", -1)]
)


st.title("Operator Training Hub")
st.markdown("Access personalized and general training videos to improve safety and efficiency.")


videos = {
    "Safety Training": [
        "https://youtu.be/sdMTxG5yDE0",
        "https://youtu.be/HGKeDBIiriU",
        "https://youtu.be/v5ErWgcMnW8",
        "https://youtu.be/bisIaARhCp0",
        "https://youtu.be/bHNDHzZ07PE",
        "https://youtu.be/G3VR0brhL1A"
    ],
    "Idling Reduction Training": [
        "https://youtu.be/XVWlTKBSurA",
        "https://youtu.be/KcPn_c7Pxsk",
        "https://youtu.be/e8heX5eH4zw",
        "https://youtu.be/-0NFpjCedis",
        "https://youtu.be/a6ZCDz05crQ"
    ],
    "Fuel Consumption Reduction Training": [
        "https://youtu.be/q7vgCojcetE",
        "https://youtu.be/JzBgvWkbvi8",
        "https://youtu.be/23MngtdOWMA"
    ],
    "General Operational Practices": [
        "https://youtu.be/uPlt7seVi9o",
        "https://youtu.be/oDKhqm3W2Pg",
        "https://youtu.be/a55VzpybLjQ",
        "https://youtu.be/3Vq-NsLGzNc"
    ]
}


def display_videos(video_list):
    cols = st.columns(2)
    for idx, url in enumerate(video_list):
        with cols[idx % 2]:
            st.video(url)


tab1, tab2, tab3 = st.tabs(["Recommended for You", "All Training Videos", "Instructor Booking"])


with tab1:
    if not latest_log:
        st.warning("No recent behavior log found.")
    else:
        timestamp_str = str(latest_log["timestamp"])
        try:
            formatted_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
        except:
            formatted_time = timestamp_str

        st.subheader(f"Machine {latest_log['Machine ID']} | {formatted_time}")
        st.markdown(f"**Safety Score:** `{latest_log['Safety Score']}`")
        st.markdown(f"**Detected Issues:** `{latest_log['Reason']}`")

        reason = latest_log["Reason"].lower()
        recommended = []

        if "seatbelt" in reason or "unsafe operation" in reason:
            st.markdown("### Safety Training: Seatbelt & Operational Protocols")
            display_videos(videos["Safety Training"][:2])
            recommended.append("Safety")

        if "idling" in reason:
            st.markdown("### Idling Reduction Training")
            display_videos(videos["Idling Reduction Training"][:2])
            recommended.append("Idling")

        if "efficiency" in reason:
            st.markdown("### Fuel Consumption Reduction Training")
            display_videos(videos["Fuel Consumption Reduction Training"][:2])
            recommended.append("Efficiency")

        if not recommended:
            st.markdown("### General Operational Practices")
            display_videos(videos["General Operational Practices"][:2])


st.subheader("All Training Video Categories")

summaries = {
    "Safety Training": {
        "English": "Seatbelts are crucial for operator safety during machine rollovers or sudden stops. Even in slow-moving machines, seatbelt use ensures operators stay protected within the machine's safety structure. Caterpillar's data shows wearing seatbelts drastically reduces injuries.",
        "Tamil": "மெஷின் கவிழ்வுகளிலும் திடீரென நிறுத்தல்களிலும் ஓட்டுநர்களை பாதுகாப்பதற்காக சீட்பெல்ட்கள் மிகவும் அவசியமானவை. மெதுவாக நகரும் இயந்திரங்களிலும் சீட்பெல்ட்கள் பாதுகாப்பு இடத்தில் ஓட்டுநரை வைத்திருக்க உதவுகின்றன. காட்டு செய்யப்பட்ட தரவுகளின்படி, சீட்பெல்ட் அணிவது காயங்களை குறைக்கிறது.",
        "Malayalam": "റോളോവർകളിലും പെട്ടെന്ന് നിൽക്കലുകളിലും ഓപ്പറേറ്റർമാരുടെ സുരക്ഷയ്ക്ക് സീറ്റ്ബെൽറ്റുകൾ നിർബന്ധമാണ്. വേഗത കുറഞ്ഞ മെഷീനുകളിലും ഇവ ഉപയോഗിക്കുന്നത് സുരക്ഷിതം. കാറ്റർപില്ലറിന്റെ ഡേറ്റ പ്രകാരം സീറ്റ്ബെൽറ്റ് ധരിക്കുന്നത് അപകടം കുറയ്ക്കുന്നു.",
        "Telugu": "యంత్రం తుప్పలు గానీ, అకస్మాత్తుగా ఆగిపోయే పరిస్థితులలో ఆపరేటర్‌ భద్రతకు సీటుబెల్ట్‌లు కీలకం. తక్కువ వేగంతో నడిచే యంత్రాలలోనూ సీటుబెల్ట్‌లు ఉపయోగించడంవల్ల రక్షణ ఉంటుంది. క్యాటర్పిల్లర్ డేటా ప్రకారం, సీటుబెల్ట్ వాడటం వల్ల గాయాలు తగ్గుతాయి."
    },
    "Idling Reduction Training": {
        "English": "Excessive engine idling causes wear equal to long-distance driving and reduces engine life. Operators are advised to avoid idling or use auto-shutdown features. Increasing RPM slightly during necessary idling reduces engine damage.",
        "Tamil": "அதிகமாக இயந்திரம் ஓய்வில் இயங்குவதால் எஞ்சின் அதிகம் kulippadu ஆகிறது. இது அதன் ஆயுளை குறைக்கும். ஓட்டுநர்கள் idling ஐ தவிர்க்க வேண்டும். அவசியமான சூழ்நிலைகளில் RPM ஐ சிறிது உயர்த்தி இயங்குதல் இழப்புகளை குறைக்கும்.",
        "Malayalam": "നീണ്ട ഇടവേളകളിൽ എഞ്ചിൻ ഐഡിൽ ചെയ്യുന്നത് അതിന്റെ ദൈർഘ്യമേറിയ ഡ്രൈവിംഗിനേക്കാൾ കൂടുതൽ കേടുപാടുകൾ വരുത്തും. ഓട്ടോ എഞ്ചിൻ ഷട്ട് ഡൗൺ സജ്ജീകരണം ഉപയോഗിക്കാൻ ഓപ്പറേറ്റർമാരെ പ്രോത്സാഹിപ്പിക്കുന്നു.",
        "Telugu": "ఇంజిన్‌ను ఎక్కువసేపు ఐడిల్ చేయడం వలన ఇది అధికంగా చెడిపోతుంది. తప్పనిసరిగా ఐడిల్ చేయాల్సిన పరిస్థితుల్లో టీఎంఐని కొద్దిగా పెంచడం వల్ల ఇంజిన్‌కు నష్టం తక్కువగా ఉంటుంది."
    },
    "Fuel Consumption Reduction Training": {
        "English": "Fuel usage depends on engine size, design, and driving behavior. Efficient acceleration and cruise control, proper air-fuel ratio, and technologies like fuel injection help optimize fuel use. Real-life hacks using magnets are also explored.",
        "Tamil": "எஞ்சின் அளவு, வடிவமைப்பு மற்றும் ஓட்டும் பழக்கம் எரிபொருள் பயன்பாட்டை தீர்மானிக்கின்றன. எரிபொருள் செலவை குறைக்க நல்ல ஓட்டுதல் மற்றும் டெக்னாலஜிகள் முக்கியம். மேக்னெட் போன்று சிறிய ஹேக்குகளும் உள்ளன.",
        "Malayalam": "എഞ്ചിനിന്റെ രൂപകൽപ്പനയും ഉപഭോഗ രീതികളും ഇന്ധന ഉപഭോഗത്തെ ബാധിക്കുന്നു. ഫ്യൂവൽ ഇൻജക്ഷൻ പോലുള്ള സാങ്കേതിക വിദ്യകളും, പൊതു ഉപദേശങ്ങളും ഉപയോഗിച്ച് ഫ്യൂവൽ ഉപഭോഗം കുറക്കാം.",
        "Telugu": "ఇంధన వినియోగం యంత్రం పరిమాణం, రూపకల్పన మరియు డ్రైవింగ్ అలవాట్లపై ఆధారపడి ఉంటుంది. ఫ్యూయల్ ఇంజెక్షన్, మెగ్నెట్‌ల వంటి చిట్కాలు వినియోగాన్ని తగ్గించడంలో ఉపయోగపడతాయి.."
    },
    "General Operational Practices": {
        "English": "Covers daily machine checks like walk-around inspection, fluid levels, and tire/track condition. Promotes alertness, safe startup/shutdown, and avoiding shortcuts to ensure long-term equipment health.",
        "Tamil": "ஒவ்வொரு நாளும் மெஷினின் நிலையை சரிபார்த்தல், திரவ அளவுகள், டயர்கள் போன்றவை பார்வையிட வேண்டும். பாதுகாப்பான செயல்பாடுகள் மற்றும் குறுக்குவழிகளை தவிர்த்தல் முக்கியம்.",
        "Malayalam": "ദിവസവും നടത്തേണ്ട പരിശോധനകളും മെഷീനിന്റെ ശരിയായ പ്രവര്‍ത്തനം ഉറപ്പുവരുത്തേണ്ട നടപടികളും ഉള്‍പ്പെടുന്നു. സുരക്ഷയും കാര്യക്ഷമതയും ഉറപ്പാക്കുന്നതിനാണ് ഈ പരിശീലനം",
        "Telugu": "ప్రతి రోజు యంత్రాన్ని తనిఖీ చేయడం, ద్రవ స్థాయిలు, టైర్‌లు/ట్రాక్‌ల స్థితి తదితరాలను పరిశీలించడం అవసరం. సరైన ప్రారంభం, ఆపటం, మరియు షార్ట్‌కట్‌లు మానుకోవడం అవసరం."
    }
}

for category, vid_list in videos.items():
    with st.expander(f"{category} ({len(vid_list)} videos)", expanded=False):
        lang = st.selectbox(f"Choose Language for {category}", ["English", "Tamil", "Malayalam", "Telugu"], key=f"{category}_lang")
        st.markdown(f"**Summary ({lang})**")
        st.info(summaries[category][lang])
        display_videos(vid_list)


with tab3:
    st.subheader("Book a Training Session with an Instructor")

    with st.form("booking_form"):
        name = st.text_input("Name")
        machine_id = st.text_input("Machine ID")
        issue = st.selectbox(
            "Training Needed On",
            ["Seatbelt & Safety", "Idling Reduction", "Fuel Efficiency", "General Operations"]
        )
        preferred_time = st.text_input("Preferred Time Slot (e.g., 3 PM - 4 PM)")
        notes = st.text_area("Additional Notes or Questions")
        submit = st.form_submit_button("Request Session")

    if submit:
        booking_data = {
            "name": name,
            "machine_id": machine_id,
            "training_topic": issue,
            "preferred_time": preferred_time,
            "notes": notes,
            "requested_at": datetime.utcnow()
        }

        db["instructor_bookings"].insert_one(booking_data)

        st.success(f"Training session requested on **{issue}** for Machine **{machine_id}**. Instructor will contact you soon.")