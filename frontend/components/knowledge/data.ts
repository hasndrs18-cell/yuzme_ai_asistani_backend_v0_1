export type KnowledgeCategory = "biomechanics" | "physiology" | "training";

export type KnowledgeDeepSection = {
  title: string;
  lead: string;
  points: string[];
};

export type KnowledgeArticle = {
  slug: string;
  title: string;
  category: KnowledgeCategory;
  categoryLabel: string;
  description: string;
  content: string;
  coachSummary: string;
  athleteSummary: string;
  commonErrors: string[];
  observationPoints: string[];
  drills: string[];
  metrics: string[];
  quickPrompts: string[];
  relatedArticles: string[];
  deepSections: KnowledgeDeepSection[];
  difficulty: "FOUNDATION" | "INTERMEDIATE" | "ADVANCED";
  readTime: number;
};

const biomechanicalTopics: readonly [string, string, string][] = [
  ["freestyle-biomechanics", "Freestyle Biomechanics", "Serbest stilde body alignment, catch, pull ve recovery fazlarının akış içindeki ilişkisi."],
  ["butterfly-biomechanics", "Butterfly Biomechanics", "Dalga aktarımı, çift kol recovery ve iki vuruşlu ritmin hidrodinamik koordinasyonu."],
  ["backstroke-biomechanics", "Backstroke Biomechanics", "Nötr baş, kalça hattı ve omuz rotasyonuyla sırtüstü streamline yönetimi."],
  ["breaststroke-biomechanics", "Breaststroke Biomechanics", "Çekiş, toparlanma, kick ve streamline fazlarının düşük sürüklemeli sıralaması."],
  ["hydrodynamic-drag", "Hydrodynamic Drag", "Hızın karesiyle büyüyen direnç kuvvetini teknik pozisyon ve ritimle azaltma."],
  ["drag-coefficient", "Drag Coefficient", "Cd değerini frontal alan, hız ve gövde pozisyonuyla birlikte yorumlama."],
  ["frontal-area-streamline", "Frontal Area & Streamline", "Baş, kalça, ayak ve kolların suya sunduğu frontal alanı azaltma rehberi."],
  ["high-elbow-catch", "High Elbow Catch", "Dirseği yüzeye yakın tutarak önkolu dikeyleştirme ve etkili yakalama."],
  ["early-vertical-forearm", "Early Vertical Forearm (EVF)", "Önkolu erken dikey konuma getirip suyu geriye yönlendirme mekanizması."],
  ["pull-phase", "Pull Phase", "Kulaçta catch sonrası basınç hattını koruyan çekiş ve gövde bağlantısı."],
  ["push-phase", "Push Phase", "Kalça hizasından çıkışa kadar itişi tamamlayıp hız kaybını azaltma."],
  ["recovery", "Recovery", "Kolu su üstünde ekonomik taşırken omuz yükünü ve giriş hazırlığını yönetme."],
  ["shoulder-rotation", "Shoulder Rotation", "Gövde ve omuz rotasyonunu hareket açıklığı, ritim ve sakatlık riskiyle dengeleme."],
  ["hip-rotation", "Hip Rotation", "Kalça rotasyonunu omuz, core ve bacak ritmiyle senkronize etme."],
  ["hand-entry-angle", "Hand Entry Angle", "Elin omuz çizgisine göre girişini kontrollü ve sessiz bir hatta düzenleme."],
  ["head-position", "Head Position", "Baş pozisyonunun boyun yükü, kalça hattı ve frontal alan üzerindeki etkisi."],
  ["body-alignment", "Body Alignment", "Baş-gövde-kalça-ayak çizgisini enerji kaçaklarını azaltacak şekilde koruma."],
  ["kick-mechanics", "Kick Mechanics", "Kalçadan başlayan, ayak bileği gevşek ve ritmik flutter/dolphin kick tekniği."],
  ["kick-frequency", "Kick Frequency", "Mesafe, stil ve yarış hedefiyle uyumlu vuruş frekansı seçimi."],
  ["stroke-length", "Stroke Length", "Kulaç uzunluğunu gereksiz kayma yerine etkili mesafe üretimiyle artırma."],
  ["stroke-rate-spm", "Stroke Rate / SPM", "Stroke rate'i stroke length ve hızla birlikte yönetme."],
  ["dps", "DPS / Distance Per Stroke", "Bir kulaç döngüsünde alınan mesafeyi ritim ve teknik kaliteyle izleme."],
  ["underwater-phase", "Underwater Phase", "Start ve dönüş sonrası streamline, dolphin kick ve breakout geçişi."],
  ["start-breakout", "Start & Breakout", "Reaksiyon, suya giriş, streamline ve ilk yüzey kulaçlarının sıralaması."],
  ["flip-turn", "Flip Turn / Dönüş Tekniği", "Yaklaşma, takla, ayak yerleşimi, itiş ve breakout zamanlaması."],
  ["finish-technique", "Finish Technique", "Son kulaçta uzanmayı bozmadan duvara temas zamanlaması ve çizgisi."],
] as const;

const physiologyTopics: readonly [string, string, string][] = [
  ["css", "CSS / Critical Swim Speed", "400 ve 200 metre testlerinden eşik çevresi pace referansı çıkarma."],
  ["css-calculation", "CSS Hesaplama", "Mesafe farkını zaman farkına bölerek m/s ve 50/100 metre pace hesaplama."],
  ["lactate-threshold", "Lactate Threshold", "Laktat üretimi ve temizlenmesinin sürdürülebilir yoğunlukla ilişkisi."],
  ["en1", "EN1", "Teknik kalite ve aerobik taban için düşük-orta yoğunluk bölgesi."],
  ["en2", "EN2", "CSS çevresinde kontrollü eşik yüklenmesi ve pace dayanıklılığı."],
  ["en3", "EN3", "Yüksek yoğunluk, yarış temposu ve laktat toleransı bölgesi."],
  ["aerobic-capacity", "Aerobic Capacity", "Oksijen kullanımı ve sürdürülebilir yüzme hacmini geliştirme."],
  ["anaerobic-capacity", "Anaerobic Capacity", "Kısa ve yüksek güç üretiminde fosfajen/glikolitik katkı."],
  ["vo2max", "VO2Max", "Maksimal oksijen kullanımını yüzme performansına bağlayan ölçüm çerçevesi."],
  ["vo2max-development", "VO2Max Development", "Yüksek aerobik güç tekrarları, dinlenme ve yüklenme progresyonu."],
  ["heart-rate-zones", "Heart Rate Zones", "Nabız, RPE ve pace verisini tek başına mutlak kural yapmadan yorumlama."],
  ["energy-systems", "Energy Systems", "ATP-PC, glikolitik ve aerobik sistemlerin mesafeye göre katkısı."],
  ["atp-pc", "ATP-PC System", "İlk saniyelerdeki kısa, yüksek güçlü üretim ve sprint başlangıcı."],
  ["glycolytic-system", "Glycolytic System", "Orta süreli yüksek yoğunlukta glikojen kullanımı ve laktat birikimi."],
  ["aerobic-system", "Aerobic System", "Uzun süreli üretim, toparlanma ve tekrarlar arası enerji desteği."],
  ["recovery-physiology", "Recovery", "Uyku, hidrasyon, düşük yoğunluk ve sinir-kas toparlanmasının izlenmesi."],
  ["overreaching", "Overreaching", "Kısa süreli planlı yüklenmeyi faydalı adaptasyona dönüştürme sınırları."],
  ["overtraining", "Overtraining", "Performans düşüşü ve kalıcı yorgunluk riskinde erken uyarı göstergeleri."],
  ["tapering", "Tapering", "Yarış öncesi hacmi azaltıp yoğunluk ve teknik hızı koruma süreci."],
  ["race-week-rest", "Yarış Haftası", "Son hafta dinlenme, aktivasyon, uyku ve seyahat yönetimi."],
  ["nutrition-hydration", "Beslenme & Hidrasyon", "Antrenman öncesi, sırası ve sonrası enerji/sıvı prensipleri."],
  ["a1-zone", "A1 / Aktif Toparlanma", "Düşük yoğunlukta kan akışını ve teknik hissi koruyan toparlanma bölgesi."],
  ["a2-zone", "A2 / Aerobik Dayanıklılık", "Temel aerobik kapasiteyi ve uzun süreli teknik kaliteyi geliştiren bölge."],
  ["sp1-zone", "SP1 / Hız ve Güç", "Kısa sprintlerde maksimum hız, sinir-kas kalitesi ve tam toparlanma bölgesi."],
  ["sp2-zone", "SP2 / Yarış Hızı", "Hedef yarış temposunu kısa tekrarlarla korumayı öğreten hız dayanıklılığı bölgesi."],
  ["sp3-zone", "SP3 / Laktat Toleransı", "Yüksek laktat altında teknik ve ritim kontrolünü geliştiren bölge."],
] as const;

const trainingTopics: readonly [string, string, string][] = [
  ["age-groups", "Age Group Methodology", "8 yaş altından Masters'a kadar gelişimsel hedeflerle antrenman planlama."],
  ["stroke-rate", "Stroke Rate by Age", "SPM değerini stil, mesafe, seviye ve hedefe göre bireyselleştirme."],
  ["set-design", "Set Design", "Amaç, mesafe, tekrar, interval, RPE ve enerji sistemini aynı sette hizalama."],
  ["drills", "Drill Library", "Fist, single-arm, 6-kick switch ve stil özel drill seçim mantığı."],
  ["aerobic-sets", "Aerobic Sets", "Hacim ve teknik kalitesini koruyan EN1 set kütüphanesi."],
  ["threshold-sets", "Threshold / CSS Sets", "CSS pace çevresinde tekrar ve dinlenme ile eşik dayanıklılığı."],
  ["sprint-sets", "Sprint Sets", "ATP-PC ve hız kalitesi için uzun dinlenmeli kısa tekrarlar."],
  ["vo2-sets", "VO2 Sets", "Yüksek aerobik güç için kontrollü yoğunluk ve teknik sınır."],
  ["lactate-tolerance-sets", "Lactate Tolerance Sets", "Laktat altında teknik çözülmeyi yönetmeye yönelik setler."],
  ["race-pace-sets", "Race Pace Sets", "Hedef mesafe split'lerini yarış ritminde tekrar etme."],
  ["technique-sets", "Technique Sets", "Düşük yorgunlukta beceri, pozisyon ve drill transferi."],
  ["recovery-sets", "Recovery Sets", "Kan akışı ve teknik hissi artıran düşük yoğunluklu uygulama."],
  ["kick-sets", "Kick Sets", "Bacak ritmi, ayak bileği ve gövde hattını geliştiren setler."],
  ["pull-sets", "Pull Sets", "Catch, EVF ve üst gövde dayanıklılığı için buoy/paddle kullanımı."],
  ["im-sets", "IM Sets", "Dört stil geçişi, enerji sistemi ve teknik esnekliği birleştiren setler."],
  ["open-water-sets", "Open Water Sets", "Navigasyon, grup ritmi, drafting ve değişken tempo yönetimi."],
  ["open-water-navigation", "Açık Su Akıntı Navigasyon Seti", "Akıntı, yön kontrolü, görüş alma ve güvenli rota seçimiyle açık su becerisi."],
  ["pacing-drafting", "Pacing & Draft Antrenmanı", "Grup içinde drafting, tempo değişimi ve enerji tasarrufunu kontrollü tekrarlarla geliştirme."],
  ["bosporus-endurance", "Boğaz Geçişi Dayanıklılık Seti", "Uzun parkurda değişken akıntı, beslenme araları ve sürdürülebilir dayanıklılık planı."],
  ["level-3-coaching", "3. Kademe Antrenörlük", "İleri teknik analiz, yarış stratejisi, LT/ANS setleri ve makro/mikro siklus planlaması."],
  ["level-4-coaching", "4. Kademe Antrenörlük", "Üst düzey biyomekanik, performans test protokolleri, blok periyotlama ve elit sporcu psikolojisi."],
  ["level-5-coaching", "5. Kademe Antrenörlük", "Olimpik düzey metodoloji, yüksek irtifa fizyolojisi, araştırma okuryazarlığı ve sistem yönetimi."],
  ["ltad-methodology", "Çocuk, Genç ve Yetişkin LTAD", "Uzun vadeli sporcu gelişimi için yaşa ve biyolojik olgunluğa göre yüzme metodolojisi."],
  ["race-strategy", "Zihinsel Hazırlık & Yarış Stratejisi", "Pacing, yarış ısınması, dikkat kontrolü ve yarış içi karar verme."],
];

const curriculumDetails: Record<string, Pick<KnowledgeArticle, "content" | "coachSummary" | "drills" | "metrics">> = {
  "level-3-coaching": {
    content: "3. kademe çalışması, teknik gözlemi yarış kararına bağlar. Giriş, catch, itiş ve toparlanma fazları aynı hız ve açıyla videoda karşılaştırılır. LT/ANS çevresindeki yüklenme CSS, nabız, RPE ve mümkünse laktat yanıtıyla kalibre edilir. Makro siklus sezon hedefini, mezo siklus 3-6 haftalık baskın uyaranı, mikro siklus ise haftalık yük-toparlanma sırasını tanımlar. Yarış stratejisinde ilk bölüm kontrolü, orta bölüm tempo ekonomisi ve son bölüm hız kaybı ayrı izlenir.",
    coachSummary: "Her yoğun setin amacı, hedef pace aralığı, tekrar arası toparlanması ve teknik başarı kriteri yazılı olmalıdır. LT/ANS setlerinde sürdürülebilir eşik ile laktat toleransı birbirine karıştırılmamalı; strateji split ve teknik gözlemle doğrulanmalıdır.",
    drills: ["Üç faz video karşılaştırması", "LT/ANS pace basamak seti", "Yarış split provası", "Laktat tolerans seti"],
    metrics: ["CSS / LT pace", "Split farkı", "RPE", "Teknik hata sayısı"],
  },
  "level-4-coaching": {
    content: "4. kademe, biyomekaniği ölçülebilir performans modeli olarak kullanır. Giriş, önkol dikeyliği, itiş yönü, eklem açıları, gövde rotasyonu ve sürtünme kaynakları aynı hareket döngüsünde incelenir. VO2max ve 7x200 metre basamak testi gibi protokoller; tek başına skor değil, antrenman reçetesinin girdisidir. Blok periyotlamada bir blokta baskın kapasite geliştirilirken diğer kapasiteler minimum etkili dozla korunur. Elit psikolojide hedef netliği, öz-düzenleme, yarış rutini ve iletişim yükü birlikte yönetilir.",
    coachSummary: "Test güvenilirliği, ölçüm protokolünün her tekrarda aynı tutulmasına bağlıdır. Açı ölçümü tek kareden yorumlanmamalı; ardışık kareler, hız bağlamı ve sporcunun ağrı/yorulma bildirimiyle birlikte değerlendirilmelidir.",
    drills: ["7x200 basamak testi", "Açı ve kuvvet aktarımı video kodlama", "Blok periyotlama mikro döngüsü", "Yarış öncesi psikolojik rutin"],
    metrics: ["VO2 yanıtı", "Eklem açıları", "Hız kaybı %", "Toparlanma süresi"],
  },
  "level-5-coaching": {
    content: "5. kademe, olimpik düzey performansı bir sistem olarak yönetir. Yüksek irtifa planlamasında hipoksik yük, uyku, hidrasyon, hemoglobin yanıtı ve deniz seviyesine dönüş zamanı kişiselleştirilir. Genetik veya biyolojik farklılıklar kesin kader gibi yorumlanmaz; araştırma bulguları etki büyüklüğü, güven aralığı ve saha uygulanabilirliğiyle okunur. Başantrenör; performans ekibi, sağlık ekibi, kulüp takvimi, etik sınırlar ve sporcu iletişimini tek karar sisteminde koordine eder.",
    coachSummary: "Olimpik plan tek laboratuvar sonucu veya moda yönteme bağlanmamalı. Performans hedefi, sağlık riski, seyahat/irtifa takvimi ve sporcunun sürdürülebilirliği aynı onay sürecinde ele alınmalıdır.",
    drills: ["Olimpik yarış simülasyonu", "İrtifa öncesi-sonrası karşılaştırma", "Performans ekibi karar toplantısı", "Araştırma bulgusu saha protokolü"],
    metrics: ["Etki büyüklüğü", "Yük-toparlanma dengesi", "Yarış güvenilirliği", "Sağlık sinyalleri"],
  },
  "ltad-methodology": {
    content: "LTAD, sporcuyu erken yaşta tek bir sonuca kilitlemek yerine hareket okuryazarlığı, teknik yeterlik, uygun yüklenme ve yaşam boyu katılım basamaklarıyla geliştirir. Çocuklarda oyun, koordinasyon ve su güvenliği; gençlerde teknik verim, kuvvet gelişimi ve yarış becerisi; yetişkinlerde bireysel hedef, sağlık durumu ve toparlanma kapasitesi öne çıkar. Biyolojik yaş, kronolojik yaştan ayrı izlenir.",
    coachSummary: "Yaş grubuna göre aynı setin mesafesi, dinlenmesi, açıklama biçimi ve başarı kriteri değiştirilmelidir. Erken uzmanlaşmayı zorunlu kılmadan dört stil, temel beceri ve sürdürülebilir motivasyon korunmalıdır.",
    drills: ["Oyun temelli streamline", "Teknik beceri istasyonu", "Yaşa göre pace basamak seti", "Yetişkin hedef-tempo seti"],
    metrics: ["Teknik kalite", "Katılım sürekliliği", "Büyüme/olgunluk", "RPE ve toparlanma"],
  },
  "race-strategy": {
    content: "Yarış stratejisi, yalnızca ilk 50 metreyi hızlı yüzmek değildir. Pacing; çıkış reaksiyonu, sualtı mesafesi, ilk bölüm hız kontrolü, dönüş verimliliği ve son bölümde hız kaybını yönetme planıdır. Zihinsel hazırlıkta uygulanabilir hedef, nefes rutini, dikkat odağı ve beklenmedik duruma B planı yarış öncesi prova edilir. Isınma, sporcunun yarış saati, havuz koşulları ve bireysel yanıtına göre kademelendirilir.",
    coachSummary: "Stratejiyi split, stroke rate, stroke length ve RPE ile doğrula. Yarış sonrası değerlendirme suçlayıcı değil, karar kalitesini artıran üç soruluk bir debrief olmalıdır: ne planlandı, ne oldu, bir sonraki prova neyi değiştirecek?",
    drills: ["25/50 pacing kontrolü", "Yarış ısınma provası", "Dikkat odağı ve nefes rutini", "Son 15 metre karar seti"],
    metrics: ["Split sapması", "Sualtı mesafesi", "Stroke rate", "Son bölüm hız kaybı"],
  },
};

function createDeepSections(title: string, description: string, category: KnowledgeCategory, index: number): KnowledgeDeepSection[] {
  const technicalLead = category === "biomechanics"
    ? `${title} için temel mekanizma; vücut pozisyonu, suya uygulanan kuvvet ve oluşan sürükleme arasındaki ilişkiyle açıklanır. Frontal alanı küçültmek, basınç farkını yönetmek ve el/önkolu etkili bir su tutuş açısında tutmak aynı anda değerlendirilmelidir.`
    : category === "physiology"
      ? `${title} enerji üretimi, yoğunluk ve toparlanma arasındaki ilişkiyi düzenler. Pace tek başına yeterli değildir; nabız, RPE, tekrar kalitesi ve set sonunda teknik bozulma birlikte okunarak bireysel yük belirlenir.`
      : `${title} antrenman kararını hedef, doz, dinlenme ve teknik transfer üzerinden yapılandırır. Bir setin değeri yalnızca toplam metrede değil, sporcunun hedeflenen beceriyi yorgunluk altında koruyabilmesinde ölçülür.`;
  const applicationLead = category === "biomechanics"
    ? "Uygulamayı önce yavaş ve kontrollü fazlara ayır, sonra tam kulaç ritmine birleştir. Aksiyoner fazda basınç hattını koru; toparlanmada eklem yükünü azalt; nefes ve ayak vuruşunu ana ritmi bozmayacak şekilde eşleştir."
    : "Uygulamayı üç basamakta ilerlet: hedef yoğunluğu tanımla, kısa tekrarlarla kaliteyi doğrula, sonra seti yaş ve seviyeye göre genişlet. Nefes, teknik ve pace hedeflerinden biri bozulduğunda yükü otomatik artırma.";
  const errors = [
    "Hedefi yalnızca hızla tanımlamak; düzeltme: teknik başarı kriterini ve kabul edilebilir pace aralığını önceden yaz.",
    "Sporcunun seviyesine uymayan mesafe veya dinlenme seçmek; düzeltme: RPE, yaş, deneyim ve son toparlanmayı doz kararına kat.",
    "Drill'i tam kulaçtan kopuk uygulamak; düzeltme: her drillin hangi faza transfer olacağını tek cümleyle belirt.",
    "Tek bir video karesinden kesin biyomekanik hüküm vermek; düzeltme: aynı fazı üç ardışık tekrar ve farklı hızlarda karşılaştır.",
    "Yorgunlukta bozulan tekniği daha fazla yükle bastırmak; düzeltme: kalite düşüşünde tekrar, mesafe veya yoğunluğu azalt.",
  ];
  const drillLevel = index % 2 === 0 ? "6 x 25, 20 saniye dinlenme; tek hedefi koru ve her tekrardan sonra bir teknik not yaz." : "8 x 50, 15-20 saniye dinlenme; ilk 25 metre beceri, ikinci 25 metre tam kulaç transferi.";
  return [
    { title: "Biyomekanik & Hidrodinamik", lead: technicalLead, points: [description, "Baş-gövde-kalça-ayak hattını göz hizası videosu ve sualtı videosuyla ayrı değerlendir.", "Sürtünme katsayısını doğrudan ölçemiyorsan streamline süresi, hız kaybı ve stroke length'i pratik göstergeler olarak kullan.", "Elin/önkolun su tutuş açısını omuz rotasyonu ve kalça hattından bağımsız yorumlama."] },
    { title: "Teknik Uygulama Adımları", lead: applicationLead, points: ["1. Başlangıç pozisyonunu kur; 2. aksiyoner fazı düşük hızda ayır; 3. toparlanma ve nefesi ekle; 4. ayak vuruşunu ritme bağla; 5. tam kulaçta aynı hissi doğrula.", "Her tekrarın sonunda pace, RPE ve bir teknik gözlem kaydet.", "Ağrı, uyuşma veya kontrol kaybında egzersizi durdur ve uygun sağlık değerlendirmesine yönlendir."] },
    { title: "Hata & Düzeltme Rehberi", lead: "Aşağıdaki beş hata sahada gözlenebilir ve tek bir komutla değil, neden-sonuç ilişkisiyle düzeltilmelidir.", points: errors },
    { title: "Kademeli Drill Serisi", lead: "Başlangıçta duyusal farkındalık, orta seviyede faz kontrolü, ileri seviyede yorgunluk altında transfer hedeflenir.", points: [`Başlangıç: ${drillLevel}`, "Orta: 4 x 50, 25 metre drill + 25 metre tam kulaç; 30 saniye dinlenme, su tutuşu ve nefes zamanlamasını koru.", "İleri: 3 x (4 x 50 hedef pace + 4 x 25 kalite); bloklar arasında 2 dakika, son tekrarda video veya antrenör geri bildirimi.", "Drill başarısı, daha güzel görünen hareket değil; aynı pace'te daha az enerji kaybı ve daha az teknik sapmadır."] },
    { title: "Antrenman & Dönemleme Yansıması", lead: "İçeriği enerji sistemi, nabız/RPE tepkisi ve yaş grubuna göre dozla; tek reçeteyi tüm sporculara uygulama.", points: [category === "physiology" ? "A1/A2 temelinde teknik ve hacim; EN1/EN2 eşiğinde sürdürülebilir pace; EN3/SP3'te kısa tekrar ve uzun toparlanma kullan." : "Teknik öğrenmede A1/A2 yükü ve yüksek tekrar kalitesi; yarışa yaklaşırken EN2/SP1 dozunu hedef mesafe ve teknik dayanıklılıkla ilişkilendir.", "Çocuklarda oyunlaştırılmış kısa bloklar ve geniş dinlenme; gençlerde beceri + kontrollü yük; yetişkinlerde sağlık, uyku ve toparlanma kapasitesine göre esneklik.", "Makro planda hedef kapasiteyi seç, mikro planda kaliteyi ölç, bir sonraki haftayı yalnızca toparlanma sinyalleri uygunsa ilerlet."] },
  ];
}

function makeArticle(tuple: readonly [string, string, string], category: KnowledgeCategory, categoryLabel: string, index: number): KnowledgeArticle {
  const [slug, title, description] = tuple;
  const related = category === "biomechanics" ? ["high-elbow-catch", "drag-coefficient", "stroke-length"] : category === "physiology" ? ["css", "lactate-threshold", "tapering"] : ["set-design", "drills", "stroke-rate"];
  const curriculum = curriculumDetails[slug];
  return {
    slug, title, category, categoryLabel, description,
    content: curriculum?.content ?? `${title}, yüzme performansını yalnızca tek bir metrikle değil; teknik kalite, yüklenme, toparlanma ve hedef mesafe bağlamıyla ele alan bir çalışma alanıdır. Bu rehber, konunun temel mekanizmasını, havuz kenarında gözlenebilir işaretlerini ve antrenmanda güvenli biçimde nasıl uygulanacağını bir araya getirir.`,
    coachSummary: curriculum?.coachSummary ?? `Antrenör için odak: ${description} Veriyi pace, RPE, teknik video ve sporcunun bireysel yanıtıyla birlikte değerlendir; SPM veya yoğunluğu herkese sabit kural olarak uygulama.`,
    athleteSummary: `Sporcu için basit anlatım: Bu konu, suda daha az enerji kaybedip hedeflediğin ritmi daha uzun süre korumana yardım eder. Önce hareketi temiz yap, sonra hızı artır.`,
    commonErrors: ["Hızı artırırken teknik hattı bozmak", "Tek bir metrikten kesin sonuç çıkarmak", "Drill'i tam kulaç hedefine aktarmadan bitirmek"],
    observationPoints: ["Hareketin tekrarlar boyunca aynı kalıyor mu?", "Pace, SPM ve RPE aynı hedefi gösteriyor mu?", "Yorgunluk geldiğinde ilk bozulan faz hangisi?"],
    drills: curriculum?.drills ?? (category === "biomechanics" ? ["Fist drill", "Single-arm / 6-kick switch", "Video ile üç faz karşılaştırması"] : category === "physiology" ? ["CSS kontrollü tekrar", "Nabız + RPE notlama", "Kolay yüzme ile aktif toparlanma"] : ["Teknik drill + tam kulaç transferi", "10 x 25 kalite tekrar", "Set sonunda kısa video kontrolü"]),
    metrics: curriculum?.metrics ?? (category === "biomechanics" ? ["Stroke length", "SPM", "DPS", "Drag / streamline"] : category === "physiology" ? ["CSS pace", "Nabız", "RPE", "Laktat / toparlanma"] : ["Mesafe", "Interval", "RPE", "Teknik kalite"]),
    quickPrompts: [`${title} nasıl geliştirilir?`, "En sık yapılan hatalar neler?", "Bunun için hangi drillleri önerirsin?", "Başlangıç seviyesinde nasıl anlatılır?", "Antrenör olarak neye dikkat etmeliyim?"],
    relatedArticles: related.filter((item) => item !== slug).slice(0, 3),
    deepSections: createDeepSections(title, description, category, index),
    difficulty: index % 3 === 0 ? "FOUNDATION" : index % 3 === 1 ? "INTERMEDIATE" : "ADVANCED",
    readTime: 5 + (index % 8),
  };
}

export const knowledgeArticles: KnowledgeArticle[] = [
  ...biomechanicalTopics.map((topic, index) => makeArticle(topic, "biomechanics", "Biyomekanik & Teknik", index)),
  ...physiologyTopics.map((topic, index) => makeArticle(topic, "physiology", "Fizyoloji & Metabolizma", index)),
  ...trainingTopics.map((topic, index) => makeArticle(topic, "training", "Antrenman Metodolojisi", index)),
];

export function getArticle(slug: string) {
  return knowledgeArticles.find((article) => article.slug === slug);
}
