const cloud = require('wx-server-sdk')
const axios = require('axios')

cloud.init({env: cloud.DYNAMIC_CURRENT_ENV})

const db = cloud.database()
const HISTORY_COLLECTION = 'userSloganHistory'
const HISTORY_LIMIT = 7

const CATEGORY_GUIDES = {
  period: '姨妈关怀，温柔克制，像熟悉的朋友轻声提醒，不出现医学化表达，不说教',
  birthday: '生日祝福，轻盈明亮，不浮夸，像把一句真心话轻轻放在今天',
  love: '恋爱纪念，甜而不腻，有陪伴感，不要网感土味情话',
  repayment: '还款提醒，理性安心，不制造压力，像在帮用户把生活打理稳妥',
  vehicle: '车辆保险，务实温和，偏安全感，不像4S店群发短信',
  pet_birthday: '宠物生日，柔软治愈，像在记录家里最可爱的成员',
  wedding: '结婚纪念，安稳长久，有日常相守感，不要夸张煽情',
  onboarding: '入职纪念，成长感与被看见感并存，鼓励但不空泛',
  festival: '自定义纪念日，留白感，生活气息，像把平凡日子轻轻点亮',
  death: '思念与缅怀，克制安静，温柔留白，不制造沉重压迫'
}

const LOCAL_POOL = {
  period: [
    '今天也别忘了先照顾自己',
    '这几天，温柔一点对待身体',
    '给自己留一点慢下来的理由',
    '热水和休息，都是今天的正经事',
    '身体在发消息，记得认真回复',
    '别硬撑，今天适合被好好照顾',
    '把节奏放轻一点，也没关系',
    '先把自己放回舒服的位置',
    '保暖、早睡、少逞强，今天就很好',
    '不舒服的时候，更要站在自己这边',
    '今天可以不那么能干',
    '把冰的先放下，把自己先顾上',
    '有点累的时候，就允许自己慢一点',
    '今天最重要的事，是别委屈身体',
    '被照顾的人，也可以先是自己',
    '别急着赶路，先让身体缓一缓',
    '一杯温热的东西，会让今天好一点',
    '身体辛苦的时候，心也要被安顿好',
    '少一点硬扛，多一点心疼自己',
    '今天适合把日子过得软一点',
    '先休息好，很多事明天再说',
    '你不是矫情，只是今天需要被温柔对待',
    '把外界的声音调小一点，听听身体',
    '今天的任务，是平稳地照顾好自己',
    '不必跟平常一样，今天有今天的节奏',
    '让肚子暖一点，心情也会慢慢松开',
    '身体不想逞强的时候，就别逼自己',
    '今天请优先选择舒服',
    '晚一点回复世界，也完全可以',
    '把自己哄好，是今天最重要的能力',
    '姨妈来的日子，更适合偏爱自己',
    '先别要求状态满分，舒服更要紧',
    '今天适合软一点、慢一点、暖一点',
    '不需要表现得没事，难受就歇一歇',
    '这几天请和自己站在同一边',
    '你可以先做一个被照顾的小孩',
    '别和不舒服较劲，顺着身体一点',
    '身体在忙，你就别再为难自己了',
    '把步子放轻，今天先过得安稳',
    '给自己一个安静一点的今天'
  ],
  birthday: [
    '愿你把今天过成喜欢的样子',
    '又长大一岁，也更值得被爱',
    '愿新的一岁，心里一直有光',
    '今天请把偏爱留给自己',
    '生日本来就是用来开心的',
    '愿你在新一岁里更松弛也更坚定',
    '把今天收进记忆里，慢慢发亮',
    '今天的你，理应被认真庆祝',
    '愿所盼都慢慢向你靠近',
    '新的一岁，先祝你平安顺意',
    '愿你继续自由，也继续柔软',
    '长大不是任务，开心才是',
    '今天适合被蛋糕、鲜花和真心围住',
    '愿你的每一岁，都不辜负自己',
    '请继续做那个眼里有光的人',
    '把生日过好，就是对生活的回应',
    '愿你被爱，也会好好爱自己',
    '新的一年，从更喜欢自己开始',
    '今天这份快乐，记得多留一点给自己',
    '愿每次许愿，都越来越接近真实的你',
    '生日快乐，愿你被温柔接住',
    '愿时间带来从容，也带来惊喜',
    '愿你把普通日子也过得有亮度',
    '今天是属于你的闪光时刻',
    '愿你这一岁，仍然保有热爱',
    '把蜡烛吹灭，也把烦恼吹远一点',
    '今天的愿望，可以先从快乐开始',
    '愿你慢慢拥有更好的自己',
    '祝你把日子过得既踏实又漂亮',
    '今天请理直气壮地收下祝福',
    '新的一岁，继续好看也好命',
    '生日这天，适合相信一点好事',
    '愿你想要的，都有回音',
    '今天请尽情做主角',
    '愿你未来每一步都走得明亮',
    '成长辛苦了，今天请好好开心',
    '愿新的一岁少些内耗，多些喜欢',
    '生日快乐，愿你一直被世界善待',
    '今天值得一切温柔和热闹',
    '把今天过好，来年就会想起它'
  ],
  love: [
    '把喜欢过成了日常，本身就很浪漫',
    '有人并肩走路，日子就会发亮',
    '爱不是热闹，是一直都在',
    '谢谢彼此，把普通一天过成纪念日',
    '喜欢你这件事，今天也算数',
    '有你在，时间好像会变柔软',
    '并肩久了，连沉默都很安心',
    '爱意不必张扬，记得就很珍贵',
    '今天也想替你记住这份偏爱',
    '把心安放在彼此身边，就是答案',
    '日子平常，但有人一起就很好',
    '喜欢从来不是一瞬间的事',
    '你在，很多普通都变成了值得',
    '相爱的人，会把细节过成证据',
    '两个人慢慢走，本身就了不起',
    '爱意最动人的样子，是一再确认',
    '今天适合重温一次心动',
    '谢谢你，让陪伴这件事有了形状',
    '一起吃饭、散步、说晚安，也很浪漫',
    '你们的日子，正在被时间温柔存档',
    '比起热烈，长久更让人心动',
    '爱不是用来说的，是被好好放在心上',
    '愿你们一直有话说，也一直愿意听',
    '在彼此身边，就是最稳的归处',
    '把日子过在一起，就是很深的告白',
    '相爱的人，总会在琐碎里发光',
    '愿今天提醒你们，再心动一次',
    '那些一起走过的路，都算答案',
    '爱意会旧吗，也许陪伴会替它续上',
    '今天适合想起当初为什么喜欢',
    '有些人出现后，时间会变得好看',
    '爱意安静下来，也还是爱意',
    '日子慢一点，有你就不算平淡',
    '愿你们继续把喜欢过成习惯',
    '一想到彼此，心就会先软下来',
    '今天也替你们记一笔温柔',
    '被放在心上，是很具体的幸福',
    '爱在场的时候，生活会变得有边有角',
    '两颗心能待在一起，本身就很难得',
    '请继续珍惜这份被认真对待的心意'
  ],
  repayment: [
    '把账理清，心也会跟着轻一点',
    '按时处理好生活，也是一种体面',
    '今天记得把这件事稳稳落下',
    '提前准备的人，日子通常更从容',
    '信用不是压力，是给未来留余地',
    '把该记得的记住，心里就不乱',
    '今天的小提醒，是替明天省心',
    '安排好数字，生活会更有底气',
    '把事情做在前面，人就会轻松很多',
    '稳稳当当地处理，也很酷',
    '先把这件小事解决，今天会更安心',
    '每一次守时，都会悄悄积累可靠',
    '提前一点准备，就少一点慌张',
    '把生活打理清楚，也是在照顾自己',
    '今天适合把该还的、该记的都理一理',
    '有条理的人，连焦虑都会少一点',
    '别让小账单占住你的心思',
    '轻轻记一笔，换来一整天踏实',
    '会安排生活的人，真的很有魅力',
    '先处理掉它，晚上会睡得更稳',
    '今天的稳妥，会变成明天的松弛',
    '生活被打理好的感觉，很治愈',
    '数字清清楚楚，心情也会跟着清爽',
    '记住这件事，是在给自己省麻烦',
    '比起临时抱佛脚，还是提前更好',
    '有些安心，是按时完成带来的',
    '今天先把这件事办妥吧',
    '把生活过明白，也是一种能力',
    '做完这一项，心里会空出很多位置',
    '先稳住琐事，才更有心力拥抱喜欢',
    '今天不拖延，明天就更轻盈',
    '小提醒不是催你，是帮你记着',
    '把该做的做好，剩下的就交给时间',
    '每一次准时，都是在替未来加分',
    '事情不大，记得就好，做完更好',
    '今天先把这一项轻轻放下',
    '安排清楚的人，也更容易快乐',
    '稳住生活的小秩序，日子会更顺',
    '别让忘记，打乱你本来的节奏',
    '这件事早点处理，心就能早点放松'
  ],
  vehicle: [
    '把保障准备好，出门也会安心些',
    '平安抵达，永远比赶时间重要',
    '车况稳一点，路上就安心一点',
    '把该续的续上，心里更踏实',
    '认真照顾车，也是认真照顾自己',
    '今天记得看看这件和安全有关的小事',
    '提前打理好，路上的风景才更轻松',
    '有准备的出行，总让人更放心',
    '平安顺路，是很值得守护的小幸福',
    '把琐事记住，旅程才更舒服',
    '这份保障在，很多担心都会少一点',
    '别等临近再慌，今天看一眼刚刚好',
    '安全感，有时候就来自提前一步',
    '照顾好座驾，也是在照顾每一次回家',
    '把该做的检查做完，路上更有底',
    '今天的小提醒，是为了以后的省心',
    '车跑得远，保障也要跟得上',
    '日常打理仔细一点，出门就从容一点',
    '别把重要的安全项留到最后一天',
    '把平安感提前准备好，是件很酷的事',
    '每一次顺利出发，背后都值得有准备',
    '车和人一样，被照顾好就更可靠',
    '今天处理一下，以后会感谢现在的自己',
    '路上平稳，就是最好听的消息',
    '把保障续上，很多事情都更稳妥',
    '有些提醒不热闹，却很有用',
    '愿每一次出门，都能平安回到家',
    '早点看一眼，心里会更有数',
    '安全这件事，什么时候认真都不算多',
    '把重要的小步骤做好，路就更宽心',
    '平安不是运气，是很多准备凑成的',
    '今天适合为下一次出发做个准备',
    '有些安心，来自你没有忘记',
    '把保障握在手里，方向盘也更稳',
    '处理完这件事，路上就多一份从容',
    '别等提醒变着急，今天就挺合适',
    '每次回家平安，都是最好的纪念',
    '车轮向前，保障也别掉队',
    '让出行变得省心，是一件温柔的事',
    '为每一段路先准备好安心'
  ],
  pet_birthday: [
    '它不会说话，却把陪伴说得很满',
    '小小生命，也值得被认真庆祝',
    '有它在，家里就多了一点柔软',
    '今天记得替这个小家伙开心一下',
    '毛孩子长大这件事，总让人心里一软',
    '陪伴是它给的，记住是你给的',
    '愿它健康撒欢，也继续依赖你',
    '家里最会治愈人的那位，又长大了',
    '谢谢它来到你的生活里',
    '有些幸福，是一开门就有人摇尾巴',
    '今天适合多摸摸它的小脑袋',
    '它的一生很短，所以每一天都很珍贵',
    '你记住它的生日，它就记住你的回家声',
    '愿它继续在你身边胡闹很久',
    '这个小生命，也在认真参与你的日子',
    '有它在，普通的一天也会变得可爱',
    '愿它继续平安、活泼、胃口好',
    '你在照顾它的时候，也被它悄悄治愈',
    '今天请把温柔多分一点给它',
    '它不是宠物，是家里会跑的小爱意',
    '毛茸茸的小日子，也值得被纪念',
    '愿它继续陪你看很多个四季',
    '家因为它，多了很多软绵绵的快乐',
    '记得这一天，就是记得它来过的可爱',
    '愿今天有零食、玩具和很多夸奖',
    '你们在彼此的生命里，都是礼物',
    '它不用懂生日，却会懂你的开心',
    '今天这份快乐，请和它一起分享',
    '小家伙长大一岁，爱也多了一点',
    '愿它一直眼睛亮亮、尾巴摇摇',
    '每一次庆祝，都是在说你很重要',
    '有它的家，总会更像家一点',
    '今天适合替它留下一个开心的瞬间',
    '愿它被世界温柔以待，也被你好好宠爱',
    '有些纪念日，毛茸茸的，也很动人',
    '今天记得告诉它：你真的很可爱',
    '谢谢它把陪伴这件事做得这么认真',
    '一岁一岁长大，一点一点把心填满',
    '爱会长出尾巴，也会在门口等你',
    '愿它继续做你生活里的小太阳'
  ],
  wedding: [
    '把喜欢过成了日子，就是很了不起的事',
    '今天适合想起那些一起走过的平常',
    '相守这件事，本身就很动人',
    '谢谢彼此，把日子过成了家',
    '走过一年又一年，爱也会长出根',
    '比起热烈，长久更难也更珍贵',
    '婚姻不是答案，是两个人一起写的过程',
    '你们把陪伴这件事做成了日常',
    '今天适合为彼此留一点时间',
    '一屋两人，已经很浪漫了',
    '很多爱都藏在一起过日子的细节里',
    '被认真选择很多次，是很深的爱',
    '岁月不说话，但它记得你们并肩',
    '一路走来，彼此都辛苦也都值得',
    '愿你们继续把平常日子过得温柔',
    '结婚纪念日，不只是纪念，也是确认',
    '有人一起回家，就是很大的幸福',
    '爱最好的样子，也许就是稳定和在场',
    '把承诺活成今天，本身就是答案',
    '今天也替你们记下这一份笃定',
    '有些浪漫，是饭后散步和一句晚安',
    '婚姻里最珍贵的，常常是没说出口的体谅',
    '你们一起过的每一年，都在发光',
    '愿以后很久很久，也还是并肩的人',
    '爱没有消失，只是慢慢变成了生活',
    '今天适合为彼此重新心动一次',
    '能把日子过在一起，已经足够浪漫',
    '愿你们在漫长里，始终有温度',
    '今天这份纪念，是平常日子的勋章',
    '爱意落进柴米油盐，也还是爱意',
    '你们在彼此身边，就是家的样子',
    '一路走来，愿温柔和默契都还在',
    '最好的纪念，是今天依然愿意并肩',
    '婚姻里那些安静的好，最值得被记住',
    '把生活过得稳稳的，也是很大的浪漫',
    '愿你们继续相看两不厌',
    '有些深情，不吵不闹，却一直都在',
    '谢谢彼此，陪对方走到今天',
    '今天的纪念，也是给未来的一句继续',
    '愿你们慢慢老去，也一直心软'
  ],
  onboarding: [
    '今天记得夸一夸一路坚持下来的自己',
    '能走到这里，已经很不容易了',
    '每一次适应，都在让你更有力量',
    '你不是突然厉害，是一步步走来的',
    '工作会留下痕迹，成长也会',
    '今天适合回头看看自己已经走了多远',
    '你在慢慢变稳，这件事很了不起',
    '那些撑住的时刻，都会变成底气',
    '成长不是一夜之间，是每天一点点',
    '愿你继续在自己的位置上发亮',
    '今天请记得，你已经比刚来时更从容了',
    '每一段职业经历，都会悄悄塑造你',
    '没有白走的路，也没有白熬的夜',
    '把这一天记下来，是在承认自己的努力',
    '工作不只是谋生，也是在慢慢成为自己',
    '你不是在原地坚持，你是在持续积累',
    '今天适合和过去那个紧张的自己打个招呼',
    '原来很多担心，后来都被你熬过来了',
    '愿你继续被看见，也继续相信自己',
    '把今天记住，是给成长一个注脚',
    '工作里那些小小进步，都很值得纪念',
    '你比想象中更能撑，也更能长大',
    '慢一点没关系，关键是你一直在向前',
    '那些看不见的努力，也都算数',
    '今天适合给自己的坚持一个名字',
    '你在变得专业，也在变得更稳',
    '不是每一天都轻松，但每一天都没有白过',
    '愿你在忙碌里，也别忘了看见自己',
    '成长有时无声，但会在某天突然回响',
    '今天请把掌声分一点给自己',
    '把职业路走成自己的路，就很厉害',
    '一路走来的你，已经值得很多肯定',
    '有些底气，正是这些日子慢慢给你的',
    '今天适合记住一句：我已经做得不错了',
    '那些不安，都被你一点点驯服了',
    '工作里的每一次坚持，都会留下光',
    '愿你继续热爱，也继续保有分寸',
    '不是非得耀眼，稳稳成长也很好',
    '把这一天记下，就是在尊重自己的努力',
    '你已经不是最初那个手忙脚乱的你了'
  ],
  festival: [
    '有些日子，被记住就会发亮',
    '普通的一天，也值得轻轻标记',
    '把日子过得有痕迹，是件很浪漫的事',
    '今天之所以特别，是因为你愿意记得',
    '生活不总要盛大，认真就已经很好',
    '给平凡留一个注脚，日子会更柔软',
    '每一个想被记住的时刻，都有意义',
    '仪式感不是麻烦，是在认真过生活',
    '今天也许普通，但以后会感谢你记下它',
    '日子被好好安放，心也会更安稳',
    '有些纪念，不是为了回头，是为了珍惜',
    '今天这笔记录，会在未来发光',
    '重要的从来不是大小，而是你在意',
    '把生活过出一点层次，需要一点记得',
    '你愿意认真，日子就会回应你',
    '今天适合给自己留下一点温柔的证据',
    '并不是特殊的日子才值得记录',
    '记住这一天，也是在记住当时的自己',
    '有些心意，写下来就不容易走散',
    '轻轻标记一下，往后会很有意义',
    '生活里的小节点，也值得被命名',
    '今天被记住，未来就会更清晰',
    '每一份在意，都值得被温柔存档',
    '把今天放进时间里，好过让它路过',
    '不是所有纪念都热闹，安静也很好',
    '今天你记住的，会成为以后的小光点',
    '为生活留白，也为生活留痕',
    '有些特别，是你赋予它的',
    '愿每个被你珍惜的日子，都有回声',
    '把平常收好，时间会替你发酵',
    '记录不是形式，是在说这一天很重要',
    '愿你一直保有认真生活的能力',
    '把日子过成有记忆点，本身就很动人',
    '有些美好，轻轻记一下就够了',
    '被放进纪念里的一天，会变得不同',
    '今天的意义，也许是以后才懂的',
    '你在为生活做一件温柔的小事',
    '这一笔记录，会在未来悄悄发亮',
    '把想留下的，认真留下',
    '生活会路过很多天，但有些天值得停一下'
  ],
  death: [
    '有些想念，不说出来也一直都在',
    '时间走得很快，思念走得很慢',
    '你没有真的离开，只是换了一种陪伴',
    '记得的人还在，故事就不会散',
    '今天适合安静地想一想你',
    '有些人走远了，却一直住在心里',
    '思念没有声音，却很长很长',
    '把这一天记住，也是在继续爱你',
    '想起你时，心里总会轻轻一软',
    '那些一起走过的时刻，还在发着微光',
    '生命会远去，留下的爱不会',
    '有些名字不常提起，却从未忘记',
    '今天的风，也许会替我问一句安好',
    '想念有时不热烈，只是一直都在',
    '你来过我的人生，这件事一直很重要',
    '把思念安静收好，也是一种陪伴',
    '有些离别过了很久，还是会想起',
    '愿回忆温柔，不再只剩下疼',
    '你不在眼前，却总在某个瞬间回来',
    '今天替你轻轻擦亮一段记忆',
    '有些爱不会结束，只会换个地方安放',
    '思念没有日期，却总会在今天靠近',
    '愿你在想起他的时候，不只有难过',
    '那些没说完的话，时间都替你记着',
    '不是遗忘才算向前，记得也可以',
    '想念一个人，本来就没有标准答案',
    '今天适合把思念放轻一点、放稳一点',
    '有些人离开后，仍旧照亮过往后的路',
    '你记得他，他就还在某处发着光',
    '有些纪念，是安静地把名字放在心里',
    '思念会来，但你也会慢慢和它相处',
    '请允许今天有一点点柔软和沉默',
    '时间不会带走一切，也会留下温度',
    '愿想起的时候，心里仍有温柔',
    '有些爱不说再见，也不会真正消失',
    '今天请轻轻地怀念，不必用力',
    '把这一天留出来，是很深的在意',
    '愿回忆慢慢从刺，变成光',
    '你没有忘记，这已经是很长情的事',
    '那些被记得的人，会一直在心上'
  ]
}

function buildPrompt(categoryId, recentSlogans) {
  const guide = CATEGORY_GUIDES[categoryId] || '温柔克制，轻盈真诚'
  const recentBlock = Array.isArray(recentSlogans) && recentSlogans.length
    ? `\n避免与这些近期文案重复或相似：\n- ${recentSlogans.join('\n- ')}`
    : ''

  return `你是一个女性向纪念日小程序的文案助手。请为 "${categoryId}" 分类生成 1 条短文案。${recentBlock}

要求：
- 只输出 1 句中文，不超过 22 个字
- 温柔、克制、有一点诗意，但不要悬浮
- 像熟悉的朋友在轻声提醒，不要像广告语
- 不要出现品牌名、日期、引号、序号
- 不要使用 emoji
- 不要过度鸡汤，不要说教
- 不要和近期文案语义重复
- 如果是姨妈相关，不出现医学审查敏感表达

直接返回文案，不要解释。`
}

function pickRandom(items) {
  if (!Array.isArray(items) || items.length === 0) return ''
  return items[Math.floor(Math.random() * items.length)]
}

function normalizeSlogan(value) {
  return String(value || '').trim().replace(/\s+/g, '')
}

async function getHistoryDoc(openid, categoryId) {
  const res = await db.collection(HISTORY_COLLECTION)
    .where({_openid: openid, categoryId})
    .limit(1)
    .get()
  return Array.isArray(res.data) && res.data.length ? res.data[0] : null
}

async function updateHistory(openid, categoryId, slogan) {
  const historyDoc = await getHistoryDoc(openid, categoryId)
  const normalized = normalizeSlogan(slogan)
  const now = Date.now()
  const prev = Array.isArray(historyDoc?.history) ? historyDoc.history : []
  const nextHistory = [
    {text: slogan, normalized, timestamp: now},
    ...prev.filter(item => {
      if (!item) return false
      const prevNormalized = item.normalized || normalizeSlogan(item.text)
      return prevNormalized !== normalized
    })
  ].slice(0, HISTORY_LIMIT)

  if (historyDoc?._id) {
    await db.collection(HISTORY_COLLECTION).doc(historyDoc._id).update({
      data: {
        history: nextHistory,
        updatedAt: db.serverDate()
      }
    })
    return nextHistory
  }

  await db.collection(HISTORY_COLLECTION).add({
    data: {
      _openid: openid,
      categoryId,
      history: nextHistory,
      createdAt: db.serverDate(),
      updatedAt: db.serverDate()
    }
  })
  return nextHistory
}

function pickFromLocalPool(categoryId, history) {
  const pool = LOCAL_POOL[categoryId] || LOCAL_POOL.festival
  const recentSet = new Set(
    (history || [])
      .map(item => {
        if (!item) return ''
        return item.normalized || normalizeSlogan(item.text)
      })
      .filter(Boolean)
  )
  const freshPool = pool.filter(text => !recentSet.has(normalizeSlogan(text)))
  return pickRandom(freshPool.length ? freshPool : pool)
}

async function callHunyuan(prompt) {
  const secretId = process.env.TENCENT_SECRET_ID
  const secretKey = process.env.TENCENT_SECRET_KEY

  if (!secretId || !secretKey) {
    throw new Error('missing model credentials')
  }

  const {TcSigner} = require('./tc-signer')
  const signer = new TcSigner({
    secretId,
    secretKey,
    service: 'hunyuan',
    version: '2023-09-01',
    action: 'InvokeModel'
  })

  const body = JSON.stringify({
    Model: 'hunyuan-standard',
    Input: {Prompt: prompt},
    Stream: false
  })

  const signed = signer.sign('POST', '/', {Body: body})

  const resp = await axios.post('https://hunyuan.tencentcloudapi.com', body, {
    headers: {
      'Content-Type': 'application/json',
      'X-Auth-Signature': signed.auth,
      'X-Auth-Nonce': signed.nonce,
      'X-Auth-Timestamp': signed.timestamp
    },
    timeout: 10000
  })

  const slogan = resp.data?.Output?.Result
  if (!slogan) {
    throw new Error('invalid model response')
  }
  return String(slogan).trim()
}

// ✅ 限流保护：每分类/用户每分钟最多3次
const _rateLimitMap = new Map()
const RATE_LIMIT_MAX = 3
const RATE_LIMIT_WINDOW_MS = 60000

function checkRateLimit(openid, categoryId) {
  const key = `${openid}::${categoryId}`
  const now = Date.now()
  const windows = _rateLimitMap.get(key) || []
  const recent = windows.filter(ts => now - ts < RATE_LIMIT_WINDOW_MS)
  if (recent.length >= RATE_LIMIT_MAX) {
    return false
  }
  recent.push(now)
  _rateLimitMap.set(key, recent)
  return true
}

exports.main = async (event, _context) => {
  const {categoryId} = event || {}
  const validIds = Object.keys(CATEGORY_GUIDES)
  const wxContext = cloud.getWXContext()
  const openid = wxContext.OPENID

  if (!categoryId || !validIds.includes(categoryId)) {
    return {success: false, error: '无效的分类ID', validIds}
  }

  // ✅ 限流检查
  if (openid && !checkRateLimit(openid, categoryId)) {
    const slogan = pickRandom(LOCAL_POOL[categoryId] || LOCAL_POOL.festival)
    return {success: true, slogan, source: 'rate-limited', categoryId}
  }

  if (!openid) {
    const slogan = pickRandom(LOCAL_POOL[categoryId] || LOCAL_POOL.festival)
    return {success: true, slogan, source: 'local-fallback', categoryId}
  }

  const historyDoc = await getHistoryDoc(openid, categoryId)
  const history = Array.isArray(historyDoc?.history) ? historyDoc.history : []
  const recentSlogans = history.map(item => item && item.text).filter(Boolean)

  let slogan = ''
  let source = 'local'

  if (process.env.TENCENT_SECRET_ID && process.env.TENCENT_SECRET_KEY) {
    try {
      slogan = await callHunyuan(buildPrompt(categoryId, recentSlogans))
      source = 'ai'
    } catch (error) {
      console.warn('get-slogan ai fallback:', error.message)
    }
  }

  if (!slogan) {
    slogan = pickFromLocalPool(categoryId, history)
    source = 'local'
  }

  await updateHistory(openid, categoryId, slogan)

  return {
    success: true,
    slogan,
    source,
    categoryId
  }
}
