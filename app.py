# --- 「道具箱」の準備 ---
# ここでは、プログラムを作るために便利な「道具（ライブラリ）」を使えるように準備（インポート）します。

import base64  # base64: 画像などのデータを、安全に送受信できる「テキスト（文字だけ）」に変換したり、元に戻したりする道具
import datetime  # datetime: 今日の日付や、今の時間を取得するための道具
import os  # os: コンピューターのファイルやフォルダを操作する（場所を調べたりする）ための道具
from io import BytesIO  # BytesIO: データを「一時的なファイル」のように扱うための道具

import requests  # requests: インターネット上のウェブサイトとやりとりする（情報を送ったり、もらったりする）ための道具
from flask import (  # flask: ウェブサイト（ホームページ）を作るための中心的な道具箱
    Flask,  # Flask: ウェブサイトの「土台」を作るための道具
    Response,  # Response: ユーザーのブラウザ（Chromeなど）に「はい、どうぞ」と返事をするための道具
    redirect,  # redirect: ユーザーを別のページに「自動で移動させる」ための道具
    render_template,  # render_template: HTMLファイル（ウェブページの設計図）を、実際のページとして表示させるための道具
    request,  # request: ユーザーが送ってきた情報（フォームに入力した内容など）を受け取るための道具
    url_for,  # url_for: ページのアドレス（URL）を正しく作るための道具
)
from fpdf import FPDF  # fpdf: PDFファイルを作成するための専門的な道具
from PIL import Image  # PIL (Image): 画像ファイルを開いたり、保存したりするための道具

# --- プログラムの「場所」に関する設定 ---
# このプログラムファイルが、コンピューターのどこにあるか（パス）を調べて、覚えておきます。
basedir = os.path.abspath(os.path.dirname(__file__))

# 「Flask」という道具を使って、ウェブサイト作りを開始します。
# 「'templates'という名前のフォルダに、HTMLファイル（ページの設計図）が入っていますよ」と教えてあげます。
app = Flask(__name__, template_folder=os.path.join(basedir, "templates"))

# --- 大事な「秘密の情報」の設定 ---
# SECRET_TOKEN: このシステムを使うための「合言葉」です。
# 他の人にバレないように、通常は「環境変数」という別の場所から読み込みます。
# （もし読み込めなかったら、"LOS" を仮の合言葉にします）
SECRET_TOKEN = os.environ.get("SECRET_TOKEN", "LOS")

# BLOB_READ_WRITE_TOKEN: データを保存する「インターネット上の倉庫（Vercel Blob）」を使うための「鍵」です。
# これも「環境変数」から読み込みます。
BLOB_READ_WRITE_TOKEN = os.environ.get("BLOB_READ_WRITE_TOKEN")

# FONT_FILE: PDFに日本語を表示するための「フォントファイル（文字のデザイン）」がどこにあるか、場所を覚えておきます。
FONT_FILE = os.path.join(basedir, "NotoSansJP-Regular.ttf")

# --- プログラム内で使う「データ」の準備 ---

# EXPLAINERS: ガイダンスを説明する担当者の名前を、言語ごとにまとめたリスト（辞書）
EXPLAINERS = {
    "vi": ["PHAM VAN THINH", "HOANG ANH NAM"],
    "id": [
        "PETRI SURYANI",
        "IMELDA SARIHUTAJULU",
        "FEBRI SAHRULLAH AHDIN",
        "MARISYA UTARI",
        "MOHAMMAD FARID HIDAYATULLAH",
        "VANESSA KOBAYASHI",
    ],
    "my": ["PYO EAINDRAY MIN", "PHYOWAI ZAW"],
    "jp": ["上林 あかり"],
    "en": ["櫻井 功"],
}

# (TRANSLATIONSとJAPANESE_TEXTのデータは長いため、内容は省略しますが、
#  TRANSLATIONS: 各言語の「翻訳データ」（ページのタイトル、説明文、ボタンの文字など）
#  JAPANESE_TEXT: 翻訳の「お手本」となる日本語のテキストデータ
#  ...という役割です)
TRANSLATIONS = { "en": { "title": "Confirmation of Preliminary Guidance", "items": [ "1. Matters concerning the content of duties, amount of remuneration, and other working conditions.", "2. Content of activities that I can perform in Japan.", "3. Matters concerning immigration procedures.", "4. Neither I, nor my spouse, lineal relatives, cohabiting relatives, or other persons in a close social relationship with me, will have money or other property managed, nor will any contract stipulating penalties for non-performance of the Specified Skilled Worker employment contract be concluded, in connection with my activities in Japan.", "5. If I have paid fees to an organization in my home country for brokerage of the Specified Skilled Worker employment contract application or for preparation for activities, I must fully understand the amount and breakdown and have agreed to it with that organization.", "6. The costs required for my support will not be borne by me, either directly or indirectly.", "7. The accepting organization must provide transportation from the port of entry or airport where I will arrive in Japan.", "8. Support for securing appropriate housing will be provided to me.", "9. A system is in place to receive consultations or complaints from me regarding my professional, daily, or social life." ], "final_confirmation": "Furthermore, regarding item 4, neither I nor my spouse, etc., have currently made any payments for security deposits or entered into contracts related to penalties, and we will not do so in the future.", "signature_label": "Signature of the Specified Skilled Worker", "agree_checkbox": "I confirm and agree to all the contents above.", "submit_button": "Submit Signature and Proceed" }, "id": { "title": "Konfirmasi Bimbingan Awal", "items": [ "1. Hal-hal mengenai isi pekerjaan, jumlah upah, dan kondisi kerja lainnya.", "2. Isi kegiatan yang dapat saya lakukan di Jepang.", "3. Hal-hal mengenai prosedur masuk ke Jepang.", "4. Saya, pasangan saya, kerabat langsung, kerabat yang tinggal bersama, atau orang lain yang memiliki hubungan sosial yang erat dengan saya tidak akan menyerahkan pengelolaan uang atau properti lainnya, dan tidak akan menandatangani kontrak yang menetapkan denda atas wanprestasi kontrak kerja Pekerja Berketerampilan Spesifik.", "5. Jika saya telah membayar biaya kepada organisasi di negara asal saya untuk perantaraan aplikasi kontrak kerja atau persiapan kegiatan, saya harus sepenuhnya memahami jumlah dan rinciannya dan telah menyetujuinya.", "6. Biaya yang diperlukan untuk dukungan saya tidak akan dibebankan kepada saya, baik secara langsung maupun tidak langsung.", "7. Organisasi penerima harus menyediakan penjemputan di pelabuhan atau bandara kedatangan saya di Jepang.", "8. Dukungan untuk mendapatkan tempat tinggal yang layak akan diberikan kepada saya.", "9. Tersedia sistem untuk menerima konsultasi atau keluhan dari saya mengenai kehidupan kerja, sehari-hari, atau sosial." ], "final_confirmation": "Selanjutnya, mengenai butir 4, saya maupun pasangan saya, dll., saat ini tidak melakukan pembayaran uang jaminan atau terikat kontrak terkait denda, dan tidak akan melakukannya di masa mendatang.", "signature_label": "Tanda Tangan Pekerja Berketerampilan Spesifik", "agree_checkbox": "Saya mengonfirmasi dan menyetujui semua isi di atas.", "submit_button": "Kirim Tanda Tangan dan Lanjutkan" }, "my": { "title": "ကြိုတင်လမ်းညွှန်ချက် အတည်ပြုလွှာ", "items": [ "၁။ ကျွန်ုပ်လုပ်ဆောင်ရမည့် လုပ်ငန်းတာဝန်များ၊ လစာပမာဏနှင့် အခြားအလုပ်သမားဆိုင်ရာ အခြေအနေများ။", "၂။ ကျွန်ုပ် ဂျပန်နိုင်ငံတွင် လုပ်ဆောင်နိုင်သော လှုပ်ရှားမှုများ၏ အကြောင်းအရာ။", "၃။ ကျွန်ုပ်၏ နိုင်ငံတွင်းဝင်ရောက်ခြင်းဆိုင်ရာ လုပ်ထုံးလုပ်နည်းများနှင့် ပတ်သက်သည့်အချက်များ။", "၄။ ကျွန်ုပ် သို့မဟုတ် ကျွန်ုပ်၏အိမ်ထောင်ဖက်၊ တိုက်ရိုက်ဆွေမျိုးများ၊ အတူနေဆွေမျိုးများ သို့မဟုတ် ကျွန်ုပ်နှင့် လူမှုရေးအရ ရင်းနှီးသောဆက်ဆံရေးရှိသူများသည် သတ်မှတ်ထားသော ကျွမ်းကျင်လုပ်သား အလုပ်ခန့်ထားမှု စာချုပ်အရ ကျွန်ုပ်၏ ဂျပန်နိုင်ငံでの လှုပ်ရှားမှုများနှင့်ဆက်စပ်၍ အာမခံငွေကောက်ခံခြင်း သို့မဟုတ် အခြားမည်သည့်အကြောင်းပြချက်ဖြင့်မဆို ငွေကြေး သို့မဟုတ် အခြားပိုင်ဆိုင်မှုများကို စီမံခန့်ခွဲခြင်းမပြုရ။ ထို့အပြင် စာချုပ်ပါအချက်များကို မလိုက်နာပါက ဒဏ်ငွေသတ်မှတ်သည့် စာချုပ်များ သို့မဟုတ် ငွေကြေးနှင့် အခြားပိုင်ဆိုင်မှုများကို မတရားလွှဲပြောင်းရန် စီစဉ်သည့် စာချုပ်များ ချုပ်ဆိုထားခြင်းမရှိသလို ချုပ်ဆိုရန် အလားအလာလည်း မရှိပါ။", "၅။ ကျွန်ုပ်သည် သတ်မှတ်ထားသော ကျွမ်းကျင်လုပ်သား အလုပ်ခန့်ထားမှုစာချုပ် လျှောက်လွှာကို ကြားခံဆောင်ရွက်ပေးခြင်း သို့မဟုတ် ကျွန်ုပ်၏နိုင်ငံရှိ အဖွဲ့အစည်းတစ်ခုသို့ လုပ်ငန်းဆောင်ရွက်မှုများအတွက် ကြိုတင်ပြင်ဆင်ခြင်းအတွက် အခကြေးငွေပေးချေခဲ့ပါက၊ ပမာဏနှင့် အသေးစိတ်အချက်အလက်များကို အပြည့်အဝနားလည်ပြီး ထိုအဖွဲ့အစည်းနှင့် သဘောတူညီမှု ရရှိထားရပါမည်။", "၆။ ကျွန်ုပ်အား ပံ့ပိုးကူညီရန် လိုအပ်သော ကုန်ကျစရိတ်များကို တိုက်ရိုက်ဖြစ်စေ၊ သွယ်ဝိုက်၍ဖြစ်စေ ကျွန်ုပ်က ကျခံမည်မဟုတ်ပါ။", "၇။ ကျွန်ုပ်အား လက်ခံသည့်အဖွဲ့အစည်းသည် ကျွန်ုပ် ဂျပန်နိုင်ငံသို့ ဆိုက်ရောက်မည့် ဆိပ်ကမ်း သို့မဟုတ် လေဆိပ်တွင် ကြိုပို့ဝန်ဆောင်မှုပေးရပါမည်။", "８။ ကျွန်ုပ်အတွက် သင့်လျော်သော နေထိုင်စရာနေရာ ရရှိရေးအတွက် အထောက်အပံ့များ ပေးအပ်ပါမည်။", "၉။ ကျွန်ုပ်၏ အလုပ်အကိုင်၊ နေ့စဉ်ဘဝ သို့မဟုတ် လူမှုဘဝနှင့်ပတ်သက်၍ တိုင်ပင်ဆွေးနွေးမှုများ သို့မဟုတ် တိုင်ကြားမှုများကို လက်ခံရန် စနစ်တစ်ခု ရှိပါသည်။" ], "final_confirmation": "ထို့အပြင်၊ အချက် ၄ နှင့်ပတ်သက်၍ ကျွန်ုပ်နှင့် ကျွန်ုပ်၏အိမ်ထောင်ဖက်စသည်တို့သည် အာမခံငွေပေးချေခြင်း သို့မဟုတ် ဒဏ်ငွေများနှင့်သက်ဆိုင်သော စာချုပ်များကို လက်ရှိတွင် ချုပ်ဆိုထားခြင်းမရှိသလို အနာဂတ်တွင်လည်း ချုပ်ဆိုမည်မဟုတ်ပါ။", "signature_label": "သတ်မှတ်ထားသော ကျွမ်းကျင်လုပ်သား၏ လက်မှတ်", "agree_checkbox": "အထက်ပါ အကြောင်းအရာအားလုံးကို ကျွန်ုပ် အတည်ပြုပြီး သဘောတူပါသည်။", "submit_button": "လက်မှတ်ထိုးပြီး ဆက်လက်ဆောင်ရွက်ပါ" }, "vi": { "title": "Giấy xác nhận Hướng dẫn Sơ bộ", "items": [ "1. Các vấn đề liên quan đến nội dung công việc, mức lương và các điều kiện lao động khác.", "2. Nội dung các hoạt động tôi có thể thực hiện tại Nhật Bản.", "3. Các vấn đề liên quan đến thủ tục nhập cảnh vào Nhật Bản.", "4. Tôi hoặc vợ/chồng, họ hàng trực hệ hoặc sống cùng, hoặc những người có quan hệ xã hội mật thiết khác với tôi, sẽ không bị quản lý tiền bạc hoặc tài sản khác liên quan đến hoạt động của tôi tại Nhật Bản theo hợp đồng lao động kỹ năng đặc định, và không ký kết bất kỳ hợp đồng nào quy định tiền phạt vi phạm hợp đồng hoặc các hợp đồng dự kiến chuyển giao tài sản bất hợp pháp khác, và dự kiến sẽ không để bị buộc ký kết.", "5. Nếu tôi đã trả phí cho một tổ chức ở nước tôi để môi giới đơn xin hợp đồng lao động hoặc để chuẩn bị cho các hoạt động, tôi phải hiểu đầy đủ số tiền và chi tiết và đã đồng ý với tổ chức đó.", "6. Các chi phí cần thiết để hỗ trợ tôi sẽ không do tôi chịu, dù trực tiếp hay gián tiếp.", "7. Tổ chức tiếp nhận phải bố trí đưa đón tôi tại cảng hoặc sân bay nơi tôi dự định nhập cảnh vào Nhật Bản.", "8. Tôi sẽ được hỗ trợ để đảm bảo nhà ở phù hợp.", "9. Có một hệ thống để tiếp nhận các cuộc tham vấn hoặc khiếu nại từ tôi liên quan đến cuộc sống nghề nghiệp, sinh hoạt hàng ngày hoặc đời sống xã hội." ], "final_confirmation": "Ngoài ra, về điều 4, tôi và vợ/chồng của tôi, v.v., hiện không thanh toán tiền đặt cọc hoặc ký kết các hợp đồng liên quan đến tiền phạt, và sẽ không làm seperti vậy trong tương lai.", "signature_label": "Chữ ký của Người lao động Kỹ năng Đặc định", "agree_checkbox": "Tôi xác nhận và đồng ý với tất cả các nội dung trên.", "submit_button": "Gửi chữ ký và Tiếp tục" }, "th": { "title": "เอกสารยืนยันการให้ข้อมูลเบื้องต้น", "items": [ "1. เรื่องที่เกี่ยวกับเนื้อหาของงาน จำนวนค่าตอบแทน และเงื่อนไขการทำงานอื่นๆ", "2. เนื้อหาของกิจกรรมที่ฉันสามารถทำได้ในญี่ปุ่น", "3. เรื่องที่เกี่ยวกับขั้นตอนการเข้าประเทศของฉัน", "4. ข้าพเจ้า คู่สมรส ญาติสายตรงหรือญาติที่อาศัยอยู่ด้วยกัน หรือบุคคลอื่นที่มีความสัมพันธ์ใกล้ชิดทางสังคมกับข้าพเจ้า จะไม่ถูกจัดการเงินหรือทรัพย์สินอื่นใดที่เกี่ยวข้องกับกิจกรรมของข้าพเจ้าในญี่ปุ่นตามสัญญาจ้างงานทักษะเฉพาะ และไม่ได้ทำสัญญาที่กำหนดค่าปรับสำหรับการไม่ปฏิบัติตามสัญญาจ้างงานหรือสัญญาอื่นใดที่คาดว่าจะมีการโอนเงินหรือทรัพย์สินอื่นโดยมิชอบ และคาดว่าจะไม่ถูกบังคับให้ทำสัญญาดังกล่าว", "5. ในกรณีที่ฉันได้จ่ายค่าใช้จ่ายให้กับหน่วยงานในประเทศของตนเองเกี่ยวกับการเป็นนายหน้าในการสมัครสัญญาจ้างงานหรือการเตรียมความพร้อมสำหรับกิจกรรมทักษะเฉพาะประเภทที่ 1 ฉันจำเป็นต้องเข้าใจจำนวนเงินและรายละเอียดอย่างถ่องแท้และได้ตกลงกับหน่วยงานนั้นๆ", "6. ค่าใช้จ่ายที่จำเป็นสำหรับการสนับสนุนของฉัน จะไม่ถูกเรียกเก็บจากฉันไม่ว่าโดยตรงหรือโดยอ้อม", "7. องค์กรต้นสังกัดทักษะเฉพาะจะต้องจัดให้มีการรับส่งฉันที่ท่าเรือหรือสนามบินที่ฉันจะเดินทางเข้าประเทศ", "8. จะมีการให้ความช่วยเหลือแก่ฉันในการจัดหาที่อยู่อาศัยที่เหมาะสม", "9. มีระบบรองรับการให้คำปรึกษาหรือการร้องทุกข์จากฉันเกี่ยวกับชีวิตการทำงาน ชีวิตประจำวัน หรือชีวิตในสังคม" ], "final_confirmation": "นอกจากนี้ เกี่ยวกับข้อ 4 ข้าพเจ้าและคู่สมรสของข้าพเจ้า ฯλฯ ไม่ได้จ่ายเงินประกันหรือทำสัญญาเกี่ยวกับค่าปรับใดๆ ในปัจจุบัน และจะไม่ทำในอนาคต", "signature_label": "ลายมือชื่อของแรงงานทักษะเฉพาะ", "agree_checkbox": "ข้าพเจ้ายืนยันและยอมรับเนื้อหาทั้งหมดข้างต้น", "submit_button": "ส่งลายมือชื่อและดำเนินการต่อ" } }
JAPANESE_TEXT = { "title": "事前ガイダンスの確認書", "items": [ "１ 私が従事する業務の内容、報酬の額その他の労働条件に関する事項", "２ 私が日本において行うことができる活動の内容", "３ 私の入国に当たっての手続に関する事項", "４ 私又は私の配偶者、直系若しくは同居の親族その他私と社会生活において密接な関係を有する者が、特定技能雇用契約に基づく私の日本における活動に関連して、保証金の徴収その他名目のいかんを問わず、金銭その他の財産を管理されず、かつ特定技能雇用契約の不履行について違約金を定める契約その他の不当に金銭その他の財産の移転を予定する契約の締結をしておらず、かつ、締結させないことが見込まれること", "５ 私が特定技能雇用契約の申込みの取次ぎ又は自国等における特定技能１号の活動の準備に関して自国等の機関に費用を支払っている場合は、その額及び内訳を十分理解して、当該機関との間で合意している必要があること", "６ 私に対し、私の支援に要する費用について、直接又は間接に負担させないこととしていること", "７ 私に対し、特定技能所属機関等が私が入国しようとする港又は飛行場において送迎を行う必要があることとなっていること", "８ 私に対し、適切な住居の確保に係る支援がされること", "９ 私からの、職業生活、日常生活又は社会生活に関する相談又は苦情の申出を受ける体制があること" ], "final_confirmation": "また、４について、私及び私の配偶者等は、保証金の支払や違約金等に係る契約を現にしておらず、また、将来にわたりしません。", }


# --- ウェブサイトの「ページ」を作る ---
# @app.route('/') は、「このウェブサイトのトップページ（住所が '/' の場所）にアクセスが来たら、
# すぐ下にある関数（def language_select():）を実行してください」という「目印」です。

@app.route("/")
def language_select():
    # ユーザーがページの住所（URL）にくっつけて送ってきた「合言葉（token）」を受け取ります。
    provided_token = request.args.get("token")
    
    # もし、受け取った合言葉が、私たちが決めた「SECRET_TOKEN」と違っていたら...
    if provided_token != SECRET_TOKEN:
        # 「アクセス権がありません。」というエラーメッセージを表示します。（403は「アクセス禁止」という意味の番号です）
        return "アクセス権がありません。", 403
    
    # 合言葉が正しければ、「language_select.html」という設計図（HTMLファイル）を使って、
    # ユーザーに「言語を選択するページ」を表示します。合言葉も一緒に渡しておきます。
    return render_template("language_select.html", token=provided_token)


# '/guidance' という住所に、'POST' という方法でアクセスが来たら、
# （'POST' とは、ユーザーがフォームで「決定」ボタンを押したときなどに使われる方法です）
@app.route("/guidance", methods=["POST"])
def guidance_page():
    # フォームから送られてきた「合言葉（token）」と「選ばれた言語（lang）」を受け取ります。
    provided_token = request.form.get("token")
    lang = request.form.get("lang")
    
    # 合言葉をチェックします。
    if provided_token != SECRET_TOKEN:
        return "アクセス権がありません。", 403
    
    # もし、言語が選ばれていなかったり、私たちが翻訳データ（TRANSLATIONS）を持っていない言語だったりしたら...
    if not lang or lang not in TRANSLATIONS:
        # エラーメッセージを表示します。（400は「あなたのリクエストが変ですよ」という意味の番号です）
        return "言語が選択されていません。", 400
    
    # すべてOKなら、「index.html」という設計図（HTMLファイル）を使って、
    # ユーザーに「ガイダンスの確認ページ」を表示します。
    return render_template(
        "index.html",
        token=provided_token,  # 合言葉
        lang=lang,  # 選ばれた言語
        translations=TRANSLATIONS[lang],  # その言語の「翻訳データ」
        japanese_text=JAPANESE_TEXT,  # 「日本語のお手本データ」
    )


# '/sign' という住所に、'POST' という方法でアクセス（署名が「送信」）されたら、
@app.route("/sign", methods=["POST"])
def sign():
    # フォームから送られてきた「合言葉（token）」と「言語（lang）」を受け取ります。
    provided_token = request.form.get("token")
    lang = request.form.get("lang")
    
    # 合言葉をチェックします。
    if provided_token != SECRET_TOKEN:
        return "不正なアクセスです。", 403

    # フォームから送られてきた「署名データ（signature_data）」を受け取ります。
    # これは「データURL」という、画像がテキスト（文字）になったものです。
    signature_data_url = request.form.get("signature_data")
    
    # もし署名データが空っぽだったら（署名されていなかったら）、
    if not signature_data_url:
        # 最初の言語選択ページに「戻します（redirect）」。
        return redirect(url_for("language_select", token=provided_token))

    # 「datetime」道具を使って、今の「日時」を取得します。
    timestamp = datetime.datetime.now()
    # 署名画像を保存するための「ファイル名」を作ります。
    # 例: "signature_20251027_102030.png" のように、日時を入れて、他のファイルと名前が被らないようにします。
    filename = f"signature_{timestamp.strftime('%Y%m%d_%H%M%S')}.png"

    # `try...except` は、「ひとまず、tryの中を実行してみて。もしエラーが出たら、exceptの中を実行してね」という命令です。
    # これで、もし失敗してもプログラム全体が止まらないようになります。
    try:
        # 署名データ（テキスト）を「,」で2つに分けます。
        # （前半は "data:image/png;base64" みたいな説明文、後半が「画像データ本体」）
        header, encoded = signature_data_url.split(",", 1)
        
        # 「base64」道具を使って、テキスト（暗号みたい）を、元の「画像データ」に戻します。
        image_data = base64.b64decode(encoded)

        # --- 「インターネット上の倉庫（Vercel Blob）」に、署名画像をアップロードする処理 ---
        
        # 倉庫に送る荷物の「送り状（headers）」を作ります。
        headers = {
            # 「この荷物は、倉庫の鍵（BLOB_READ_WRITE_TOKEN）を使って送ります」
            "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
            # 「荷物の中身は、PNG画像です」
            "Content-Type": "image/png",
        }
        # 倉庫の「荷物を置く場所（アップロード先のURL）」を指定します。
        upload_url = f"https://blob.vercel-storage.com/{filename}"

        # 「requests」道具を使って、指定した場所に、画像データ（image_data）を
        # 「送り状（headers）」付きで「送ります（put）」。
        response = requests.put(upload_url, data=image_data, headers=headers)
        
        # もし、アップロードが失敗したら（例：倉庫の鍵が間違っていたら）、
        # ここでエラーを発生させて、下の「except」にジャンプさせます。
        response.raise_for_status()

        # アップロードが成功したら、倉庫からの「返事（response）」を調べます。
        # 返事の中から、アップロードされた画像の「公開URL（誰でも見られるアドレス）」を取り出します。
        public_url = response.json().get("url")
        
        # もし、なぜか公開URLが返事に含まれていなかったら...
        if not public_url:
            # 自分たちでエラーを発生させて、「except」にジャンプさせます。
            raise Exception("Blob upload response did not contain a URL.")

    # もし、`try` の中で何かエラーが起きたら（例：アップロード失敗、URLが取れない）...
    except Exception as e:
        # 「どんなエラーが起きたか」を、こっそり記録（print）しておきます。（ユーザーには見えません）
        print(f"Error uploading signature to Blob: {e}")
        # ユーザーには「失敗しました」というメッセージを表示します。
        return "署名画像のアップロードに失敗しました。", 500

    # すべてが成功したら、ユーザーを「/download_page（ダウンロード準備ページ）」に移動させます。
    # そのとき、さっき取得した「画像の公開URL」と「言語」を、次のページに渡します。
    return redirect(url_for("download_page", signature_url=public_url, lang=lang))


# '/download' という住所にアクセスが来たら、
@app.route("/download")
def download_page():
    # 前のページから渡された「署名画像のURL（signature_url）」と「言語（lang）」を受け取ります。
    signature_url = request.args.get("signature_url")
    lang = request.args.get("lang")
    
    # もし、どちらかの情報が足りなかったら...
    if not signature_url or not lang:
        # エラーメッセージを表示します。
        return "必要な情報が不足しています。", 400

    # 最初に準備した「EXPLAINERS（説明者リスト）」から、
    # 「選ばれた言語の説明者」と「日本語の説明者（'jp'）」の両方のリストを取り出します。
    available_explainers = EXPLAINERS.get(lang, []) + EXPLAINERS.get("jp", [])
    
    # 2つのリストを足したので、もし名前がダブっていたら、
    # `set()` で重複をなくしてから、もう一度 `list()` でリストに戻します。
    unique_explainers = list(set(available_explainers))

    # 「download.html」という設計図（HTMLファイル）を使って、
    # ユーザーに「説明者を選ぶページ」を表示します。
    return render_template(
        "download.html",
        signature_url=signature_url,  # 署名画像のURL（次のPDF作成で使います）
        explainers=unique_explainers,  # 説明者のリスト（選択肢として使います）
    )


# '/generate-pdf' という住所に、'POST' という方法でアクセス（「PDF作成」ボタンが押）されたら、
@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():
    # フォームから送られてきた「署名画像のURL」と「選ばれた説明者の名前」を受け取ります。
    signature_url = request.form.get("signature_url")
    explainer_name = request.form.get("explainer_name")

    # もし、どちらかの情報が足りなかったら...
    if not signature_url or not explainer_name:
        # エラーメッセージを表示します。
        return "必要な情報が不足しています。", 400

    # また `try...except` を使います。（今度は、画像を「ダウンロード」する処理です）
    try:
        # --- 「インターネット上の倉庫（Vercel Blob）」から、署名画像をダウンロードする処理 ---
        
        # 「requests」道具を使って、指定されたURL（signature_url）から「画像をもらってきます（get）」。
        response = requests.get(signature_url)
        # もしダウンロードが失敗したら（例：URLが間違っていたら）、エラーを発生させます。
        response.raise_for_status()
        # ダウンロードした「画像データ本体」を取り出します。
        signature_image_data = response.content

        # 「PIL (Image)」道具を使って、ダウンロードした画像データを開きます。
        signature_image = Image.open(BytesIO(signature_image_data))
        
        # 画像を「一時的なファイル」として、サーバー（プログラムが動いている場所）に保存します。
        # (Vercelという環境では、"/tmp" というフォルダにしか保存できないルールになっています)
        temp_signature_path = f"/tmp/{os.path.basename(signature_url)}"
        signature_image.save(temp_signature_path)

    # もし、`try` の中でエラーが起きたら（例：ダウンロード失敗）...
    except Exception as e:
        # エラーをこっそり記録します。
        print(f"Error downloading signature from Blob: {e}")
        # ユーザーに「失敗しました」と伝えます。
        return "署名画像の取得に失敗しました。", 404

    # --- PDFを作成する処理 ---
    
    # 「FPDF」道具を使って、PDFの「真っ白な紙」を準備します。
    pdf = FPDF()
    # 1ページ目を追加します。
    pdf.add_page()
    # このPDFで「NotoSansJP」という名前で、さっき指定した「日本語フォントファイル」を使えるように登録します。
    pdf.add_font("NotoSansJP", "", FONT_FILE)

    # --- PDFの見た目（レイアウト）を作る ---
    # (ここからは、PDFに文字や線を書き込んでいく、お絵かきのような作業です)
    
    # フォントを「NotoSansJP」のサイズ10に設定
    pdf.set_font("NotoSansJP", "", 10)
    # ページの左上（X=左端, Y=10mm）に移動
    pdf.set_xy(pdf.l_margin, 10)
    # 「参考様式第５－９号」という文字を書きます (align='L'は左寄せ)
    pdf.cell(0, 10, "参考様式第５－９号", align="L")
    
    # Y=25mm の位置に移動
    pdf.set_xy(0, 25)
    # フォントサイズを16に変更
    pdf.set_font("NotoSansJP", "", 16)
    # ページの真ん中（align='C'）にタイトルを書きます。
    # new_x, new_yは「書いた後に、次の行の先頭に移動する」という意味です。
    pdf.cell(0, 10, "事 前 ガ イ ダ ン ス の 確 認 書", new_x="LMARGIN", new_y="NEXT", align="C")
    
    # 12mmのすき間をあけます。
    pdf.ln(12)
    # フォントサイズを10.5に戻します。
    pdf.set_font("NotoSansJP", "", 10.5)
    
    # 確認項目のリスト（日本語）
    list_items = [("１", "私が従事する業務の内容、報酬の額その他の労働条件に関する事項"),("２", "私が日本において行うことができる活動の内容"),("３", "私の入国に当たっての手続に関する事項"),("４", "私又は私の配偶者、直系若しくは同居の親族その他私と社会生活において密接な関係を有する者が、特定技能雇用契約に基づく私の日本における活動に関連して、保証金の徴収その他名目のいかんを問わず、金銭その他の財産を管理されず、かつ特定技能雇用契約の不履行について違約金を定める契約その他の不当に金銭その他の財産の移転を予定する契約の締結をしておらず、かつ、締結させないことが見込まれること"),("５", "私が特定技能雇用契約の申込みの取次ぎ又は自国等における特定技能１号の活動の準備に関して自国等の機関に費用を支払っている場合は、その額及び内訳を十分理解して、当該機関との間で合意している必要があること"),("６", "私に対し、私の支援に要する費用について、直接又は間接に負担させないこととしていること"),("７", "私に対し、特定技能所属機関等が私が入国しようとする港又は飛行場において送迎を行う必要があることとなっていること"),("８", "私に対し、適切な住居の確保に係る支援がされること"),("９", "私からの、職業生活、日常生活又は社会生活に関する相談又は苦情の申出を受ける体制があること")]
    
    # 最初の左端の位置（X座標）を覚えておきます。
    initial_x = pdf.get_x()
    
    # リストの項目を、ひとつずつPDFに書き出します。
    for number, text in list_items:
        pdf.set_x(initial_x)  # 左端の位置をそろえます。
        pdf.cell(8, 5, number, align="L")  # まず「番号」（１、２...）を書きます。
        # `multi_cell` は、長い文章を「自動で折り返して」書いてくれる道具です。
        pdf.multi_cell(pdf.w - pdf.l_margin - pdf.r_margin - 8, 5, text, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)  # 少しだけすき間をあけます。

    # ...（ここからも、日付や説明者名、下線などをPDFに書き込む処理が続きます）...
    
    pdf.set_font_size(11)
    pdf.ln(8)
    pdf.multi_cell(0, 8, "について、")
    pdf.ln(1)
    today = datetime.date.today()
    # 文字列内の全角スペースを半角2スペースに修正
    date_time_str = f"{today.year}年{today.month}月{today.day}日  13時00分から16時00分まで"
    text_width = pdf.get_string_width(date_time_str)
    start_x = (pdf.w - text_width) / 2
    pdf.cell(0, 8, date_time_str, new_x="LMARGIN", new_y="NEXT", align="C")
    y_pos = pdf.get_y()
    pdf.line(start_x, y_pos - 1, start_x + text_width, y_pos - 1)
    pdf.ln(4)
    underline_length = 80
    indent = 70
    pdf.cell(0, 8, "特定技能所属機関（又は登録支援機関）の氏名又は名称", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    text_to_underline = "レバレジーズオフィスサポート株式会社"
    pdf.set_x(pdf.l_margin + indent)
    pdf.cell(underline_length, 8, text_to_underline, new_x="LMARGIN", new_y="NEXT")
    y_pos = pdf.get_y()
    pdf.line(pdf.l_margin + indent, y_pos - 1, pdf.l_margin + indent + underline_length, y_pos - 1)
    pdf.ln(4)
    pdf.cell(0, 8, "説明者の氏名", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    # ここで、ユーザーが選んだ「説明者の名前」を使います。
    text_to_underline = explainer_name
    pdf.set_x(pdf.l_margin + indent)
    pdf.cell(underline_length, 8, text_to_underline, new_x="LMARGIN", new_y="NEXT")
    y_pos = pdf.get_y()
    pdf.line(pdf.l_margin + indent, y_pos - 1, pdf.l_margin + indent + underline_length, y_pos - 1)
    pdf.ln(4)
    pdf.multi_cell(0, 8, "から説明を受け、内容を十分に理解しました。")
    pdf.ln(2)
    pdf.multi_cell(0, 8, "また、４について、私及び私の配偶者等は、保証金の支払や違約金等に係る契約を現にしておらず、また、将来にわたりしません。")
    
    # 署名欄のレイアウト
    date_str = f"{today.year}年{today.month}月{today.day}日"
    sig_y_pos = pdf.h - 35  # ページの下から35mmの位置
    pdf.set_y(sig_y_pos)
    pdf.cell(45, 8, "特定技能外国人の署名")
    line_start_x = pdf.get_x()
    line_end_x = line_start_x + 65
    pdf.line(line_start_x, sig_y_pos + 7, line_end_x, sig_y_pos + 7)  # 署名のための下線
    
    # `pdf.image` で、さっき一時保存した「署名画像」をPDFに貼り付けます。
    pdf.image(temp_signature_path, x=line_start_x + 5, y=sig_y_pos - 10, w=55, h=15)
    
    pdf.set_xy(line_end_x + 5, sig_y_pos)
    pdf.cell(0, 8, date_str, align="R")  # 右寄せで日付を記載

    # --- PDFの完成と後片付け ---
    
    # PDFの「データ」を完成させます。
    pdf_output = bytes(pdf.output())

    # （おまけ）完成したPDFも、「インターネット上の倉庫（Vercel Blob）」にアップロードしておきます。
    try:
        # PDFのファイル名を、元の署名画像の名前に合わせて作ります。
        pdf_filename = os.path.splitext(os.path.basename(signature_url))[0] + ".pdf"
        
        # 再び「送り状（headers）」を準備します。（今度は "application/pdf" です）
        headers = {
            "Authorization": f"Bearer {BLOB_READ_WRITE_TOKEN}",
            "Content-Type": "application/pdf",
        }
        upload_url = f"https://blob.vercel-storage.com/{pdf_filename}"
        
        # PDFデータをアップロードします。
        response = requests.put(upload_url, data=pdf_output, headers=headers)
        response.raise_