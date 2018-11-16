!function(e,a){"object"==typeof exports&&"undefined"!=typeof module?module.exports=a():"function"==typeof define&&define.amd?define(a):e.anchorme=a()}(this,function(){"use strict";function e(e,a){return a={exports:{}},e(a,a.exports),a.exports}var a=e(function(e,a){function n(e){return e||(e={attributes:[],ips:!0,emails:!0,urls:!0,files:!0,truncate:1/0,defaultProtocol:"http://",list:!1}),"object"!=typeof e.attributes&&(e.attributes=[]),"boolean"!=typeof e.ips&&(e.ips=!0),"boolean"!=typeof e.emails&&(e.emails=!0),"boolean"!=typeof e.urls&&(e.urls=!0),"boolean"!=typeof e.files&&(e.files=!0),"boolean"!=typeof e.list&&(e.list=!1),"string"!=typeof e.defaultProtocol&&"function"!=typeof e.defaultProtocol&&(e.defaultProtocol="http://"),"number"==typeof e.truncate||"object"==typeof e.truncate&&null!==e.truncate||(e.truncate=1/0),e}function t(e){return!isNaN(Number(e))&&!(Number(e)>65535)}Object.defineProperty(a,"__esModule",{value:!0}),a.defaultOptions=n,a.isPort=t}),n=e(function(e,a){Object.defineProperty(a,"__esModule",{value:!0}),a.tlds=["com","org","net","uk","gov","edu","io","cc","co","aaa","aarp","abarth","abb","abbott","abbvie","abc","able","abogado","abudhabi","ac","academy","accenture","accountant","accountants","aco","active","actor","ad","adac","ads","adult","ae","aeg","aero","aetna","af","afamilycompany","afl","africa","ag","agakhan","agency","ai","aig","aigo","airbus","airforce","airtel","akdn","al","alfaromeo","alibaba","alipay","allfinanz","allstate","ally","alsace","alstom","am","americanexpress","americanfamily","amex","amfam","amica","amsterdam","analytics","android","anquan","anz","ao","aol","apartments","app","apple","aq","aquarelle","ar","aramco","archi","army","arpa","art","arte","as","asda","asia","associates","at","athleta","attorney","au","auction","audi","audible","audio","auspost","author","auto","autos","avianca","aw","aws","ax","axa","az","azure","ba","baby","baidu","banamex","bananarepublic","band","bank","bar","barcelona","barclaycard","barclays","barefoot","bargains","baseball","basketball","bauhaus","bayern","bb","bbc","bbt","bbva","bcg","bcn","bd","be","beats","beauty","beer","bentley","berlin","best","bestbuy","bet","bf","bg","bh","bharti","bi","bible","bid","bike","bing","bingo","bio","biz","bj","black","blackfriday","blanco","blockbuster","blog","bloomberg","blue","bm","bms","bmw","bn","bnl","bnpparibas","bo","boats","boehringer","bofa","bom","bond","boo","book","booking","boots","bosch","bostik","boston","bot","boutique","box","br","bradesco","bridgestone","broadway","broker","brother","brussels","bs","bt","budapest","bugatti","build","builders","business","buy","buzz","bv","bw","by","bz","bzh","ca","cab","cafe","cal","call","calvinklein","cam","camera","camp","cancerresearch","canon","capetown","capital","capitalone","car","caravan","cards","care","career","careers","cars","cartier","casa","case","caseih","cash","casino","cat","catering","catholic","cba","cbn","cbre","cbs","cd","ceb","center","ceo","cern","cf","cfa","cfd","cg","ch","chanel","channel","chase","chat","cheap","chintai","chloe","christmas","chrome","chrysler","church","ci","cipriani","circle","cisco","citadel","citi","citic","city","cityeats","ck","cl","claims","cleaning","click","clinic","clinique","clothing","cloud","club","clubmed","cm","cn","coach","codes","coffee","college","cologne","comcast","commbank","community","company","compare","computer","comsec","condos","construction","consulting","contact","contractors","cooking","cookingchannel","cool","coop","corsica","country","coupon","coupons","courses","cr","credit","creditcard","creditunion","cricket","crown","crs","cruise","cruises","csc","cu","cuisinella","cv","cw","cx","cy","cymru","cyou","cz","dabur","dad","dance","data","date","dating","datsun","day","dclk","dds","de","deal","dealer","deals","degree","delivery","dell","deloitte","delta","democrat","dental","dentist","desi","design","dev","dhl","diamonds","diet","digital","direct","directory","discount","discover","dish","diy","dj","dk","dm","dnp","do","docs","doctor","dodge","dog","doha","domains","dot","download","drive","dtv","dubai","duck","dunlop","duns","dupont","durban","dvag","dvr","dz","earth","eat","ec","eco","edeka","education","ee","eg","email","emerck","energy","engineer","engineering","enterprises","epost","epson","equipment","er","ericsson","erni","es","esq","estate","esurance","et","eu","eurovision","eus","events","everbank","exchange","expert","exposed","express","extraspace","fage","fail","fairwinds","faith","family","fan","fans","farm","farmers","fashion","fast","fedex","feedback","ferrari","ferrero","fi","fiat","fidelity","fido","film","final","finance","financial","fire","firestone","firmdale","fish","fishing","fit","fitness","fj","fk","flickr","flights","flir","florist","flowers","fly","fm","fo","foo","food","foodnetwork","football","ford","forex","forsale","forum","foundation","fox","fr","free","fresenius","frl","frogans","frontdoor","frontier","ftr","fujitsu","fujixerox","fun","fund","furniture","futbol","fyi","ga","gal","gallery","gallo","gallup","game","games","gap","garden","gb","gbiz","gd","gdn","ge","gea","gent","genting","george","gf","gg","ggee","gh","gi","gift","gifts","gives","giving","gl","glade","glass","gle","global","globo","gm","gmail","gmbh","gmo","gmx","gn","godaddy","gold","goldpoint","golf","goo","goodhands","goodyear","goog","google","gop","got","gp","gq","gr","grainger","graphics","gratis","green","gripe","group","gs","gt","gu","guardian","gucci","guge","guide","guitars","guru","gw","gy","hair","hamburg","hangout","haus","hbo","hdfc","hdfcbank","health","healthcare","help","helsinki","here","hermes","hgtv","hiphop","hisamitsu","hitachi","hiv","hk","hkt","hm","hn","hockey","holdings","holiday","homedepot","homegoods","homes","homesense","honda","honeywell","horse","hospital","host","hosting","hot","hoteles","hotmail","house","how","hr","hsbc","ht","htc","hu","hughes","hyatt","hyundai","ibm","icbc","ice","icu","id","ie","ieee","ifm","ikano","il","im","imamat","imdb","immo","immobilien","in","industries","infiniti","info","ing","ink","institute","insurance","insure","int","intel","international","intuit","investments","ipiranga","iq","ir","irish","is","iselect","ismaili","ist","istanbul","it","itau","itv","iveco","iwc","jaguar","java","jcb","jcp","je","jeep","jetzt","jewelry","jio","jlc","jll","jm","jmp","jnj","jo","jobs","joburg","jot","joy","jp","jpmorgan","jprs","juegos","juniper","kaufen","kddi","ke","kerryhotels","kerrylogistics","kerryproperties","kfh","kg","kh","ki","kia","kim","kinder","kindle","kitchen","kiwi","km","kn","koeln","komatsu","kosher","kp","kpmg","kpn","kr","krd","kred","kuokgroup","kw","ky","kyoto","kz","la","lacaixa","ladbrokes","lamborghini","lamer","lancaster","lancia","lancome","land","landrover","lanxess","lasalle","lat","latino","latrobe","law","lawyer","lb","lc","lds","lease","leclerc","lefrak","legal","lego","lexus","lgbt","li","liaison","lidl","life","lifeinsurance","lifestyle","lighting","like","lilly","limited","limo","lincoln","linde","link","lipsy","live","living","lixil","lk","loan","loans","locker","locus","loft","lol","london","lotte","lotto","love","lpl","lplfinancial","lr","ls","lt","ltd","ltda","lu","lundbeck","lupin","luxe","luxury","lv","ly","ma","macys","madrid","maif","maison","makeup","man","management","mango","market","marketing","markets","marriott","marshalls","maserati","mattel","mba","mc","mcd","mcdonalds","mckinsey","md","me","med","media","meet","melbourne","meme","memorial","men","menu","meo","metlife","mg","mh","miami","microsoft","mil","mini","mint","mit","mitsubishi","mk","ml","mlb","mls","mm","mma","mn","mo","mobi","mobile","mobily","moda","moe","moi","mom","monash","money","monster","montblanc","mopar","mormon","mortgage","moscow","moto","motorcycles","mov","movie","movistar","mp","mq","mr","ms","msd","mt","mtn","mtpc","mtr","mu","museum","mutual","mv","mw","mx","my","mz","na","nab","nadex","nagoya","name","nationwide","natura","navy","nba","nc","ne","nec","netbank","netflix","network","neustar","new","newholland","news","next","nextdirect","nexus","nf","nfl","ng","ngo","nhk","ni","nico","nike","nikon","ninja","nissan","nissay","nl","no","nokia","northwesternmutual","norton","now","nowruz","nowtv","np","nr","nra","nrw","ntt","nu","nyc","nz","obi","observer","off","office","okinawa","olayan","olayangroup","oldnavy","ollo","om","omega","one","ong","onl","online","onyourside","ooo","open","oracle","orange","organic","orientexpress","origins","osaka","otsuka","ott","ovh","pa","page","pamperedchef","panasonic","panerai","paris","pars","partners","parts","party","passagens","pay","pccw","pe","pet","pf","pfizer","pg","ph","pharmacy","philips","phone","photo","photography","photos","physio","piaget","pics","pictet","pictures","pid","pin","ping","pink","pioneer","pizza","pk","pl","place","play","playstation","plumbing","plus","pm","pn","pnc","pohl","poker","politie","porn","post","pr","pramerica","praxi","press","prime","pro","prod","productions","prof","progressive","promo","properties","property","protection","pru","prudential","ps","pt","pub","pw","pwc","py","qa","qpon","quebec","quest","qvc","racing","radio","raid","re","read","realestate","realtor","realty","recipes","red","redstone","redumbrella","rehab","reise","reisen","reit","reliance","ren","rent","rentals","repair","report","republican","rest","restaurant","review","reviews","rexroth","rich","richardli","ricoh","rightathome","ril","rio","rip","rmit","ro","rocher","rocks","rodeo","rogers","room","rs","rsvp","ru","ruhr","run","rw","rwe","ryukyu","sa","saarland","safe","safety","sakura","sale","salon","samsclub","samsung","sandvik","sandvikcoromant","sanofi","sap","sapo","sarl","sas","save","saxo","sb","sbi","sbs","sc","sca","scb","schaeffler","schmidt","scholarships","school","schule","schwarz","science","scjohnson","scor","scot","sd","se","seat","secure","security","seek","select","sener","services","ses","seven","sew","sex","sexy","sfr","sg","sh","shangrila","sharp","shaw","shell","shia","shiksha","shoes","shop","shopping","shouji","show","showtime","shriram","si","silk","sina","singles","site","sj","sk","ski","skin","sky","skype","sl","sling","sm","smart","smile","sn","sncf","so","soccer","social","softbank","software","sohu","solar","solutions","song","sony","soy","space","spiegel","spot","spreadbetting","sr","srl","srt","st","stada","staples","star","starhub","statebank","statefarm","statoil","stc","stcgroup","stockholm","storage","store","stream","studio","study","style","su","sucks","supplies","supply","support","surf","surgery","suzuki","sv","swatch","swiftcover","swiss","sx","sy","sydney","symantec","systems","sz","tab","taipei","talk","taobao","target","tatamotors","tatar","tattoo","tax","taxi","tc","tci","td","tdk","team","tech","technology","tel","telecity","telefonica","temasek","tennis","teva","tf","tg","th","thd","theater","theatre","tiaa","tickets","tienda","tiffany","tips","tires","tirol","tj","tjmaxx","tjx","tk","tkmaxx","tl","tm","tmall","tn","to","today","tokyo","tools","top","toray","toshiba","total","tours","town","toyota","toys","tr","trade","trading","training","travel","travelchannel","travelers","travelersinsurance","trust","trv","tt","tube","tui","tunes","tushu","tv","tvs","tw","tz","ua","ubank","ubs","uconnect","ug","unicom","university","uno","uol","ups","us","uy","uz","va","vacations","vana","vanguard","vc","ve","vegas","ventures","verisign","versicherung","vet","vg","vi","viajes","video","vig","viking","villas","vin","vip","virgin","visa","vision","vista","vistaprint","viva","vivo","vlaanderen","vn","vodka","volkswagen","volvo","vote","voting","voto","voyage","vu","vuelos","wales","walmart","walter","wang","wanggou","warman","watch","watches","weather","weatherchannel","webcam","weber","website","wed","wedding","weibo","weir","wf","whoswho","wien","wiki","williamhill","win","windows","wine","winners","wme","wolterskluwer","woodside","work","works","world","wow","ws","wtc","wtf","xbox","xerox","xfinity","xihuan","xin","xn--11b4c3d","xn--1ck2e1b","xn--1qqw23a","xn--30rr7y","xn--3bst00m","xn--3ds443g","xn--3e0b707e","xn--3oq18vl8pn36a","xn--3pxu8k","xn--42c2d9a","xn--45brj9c","xn--45q11c","xn--4gbrim","xn--54b7fta0cc","xn--55qw42g","xn--55qx5d","xn--5su34j936bgsg","xn--5tzm5g","xn--6frz82g","xn--6qq986b3xl","xn--80adxhks","xn--80ao21a","xn--80aqecdr1a","xn--80asehdb","xn--80aswg","xn--8y0a063a","xn--90a3ac","xn--90ae","xn--90ais","xn--9dbq2a","xn--9et52u","xn--9krt00a","xn--b4w605ferd","xn--bck1b9a5dre4c","xn--c1avg","xn--c2br7g","xn--cck2b3b","xn--cg4bki","xn--clchc0ea0b2g2a9gcd","xn--czr694b","xn--czrs0t","xn--czru2d","xn--d1acj3b","xn--d1alf","xn--e1a4c","xn--eckvdtc9d","xn--efvy88h","xn--estv75g","xn--fct429k","xn--fhbei","xn--fiq228c5hs","xn--fiq64b","xn--fiqs8s","xn--fiqz9s","xn--fjq720a","xn--flw351e","xn--fpcrj9c3d","xn--fzc2c9e2c","xn--fzys8d69uvgm","xn--g2xx48c","xn--gckr3f0f","xn--gecrj9c","xn--gk3at1e","xn--h2brj9c","xn--hxt814e","xn--i1b6b1a6a2e","xn--imr513n","xn--io0a7i","xn--j1aef","xn--j1amh","xn--j6w193g","xn--jlq61u9w7b","xn--jvr189m","xn--kcrx77d1x4a","xn--kprw13d","xn--kpry57d","xn--kpu716f","xn--kput3i","xn--l1acc","xn--lgbbat1ad8j","xn--mgb9awbf","xn--mgba3a3ejt","xn--mgba3a4f16a","xn--mgba7c0bbn0a","xn--mgbaam7a8h","xn--mgbab2bd","xn--mgbai9azgqp6j","xn--mgbayh7gpa","xn--mgbb9fbpob","xn--mgbbh1a71e","xn--mgbc0a9azcg","xn--mgbca7dzdo","xn--mgberp4a5d4ar","xn--mgbi4ecexp","xn--mgbpl2fh","xn--mgbt3dhd","xn--mgbtx2b","xn--mgbx4cd0ab","xn--mix891f","xn--mk1bu44c","xn--mxtq1m","xn--ngbc5azd","xn--ngbe9e0a","xn--node","xn--nqv7f","xn--nqv7fs00ema","xn--nyqy26a","xn--o3cw4h","xn--ogbpf8fl","xn--p1acf","xn--p1ai","xn--pbt977c","xn--pgbs0dh","xn--pssy2u","xn--q9jyb4c","xn--qcka1pmc","xn--qxam","xn--rhqv96g","xn--rovu88b","xn--s9brj9c","xn--ses554g","xn--t60b56a","xn--tckwe","xn--tiq49xqyj","xn--unup4y","xn--vermgensberater-ctb","xn--vermgensberatung-pwb","xn--vhquv","xn--vuq861b","xn--w4r85el8fhu5dnra","xn--w4rs40l","xn--wgbh1c","xn--wgbl6a","xn--xhq521b","xn--xkc2al3hye2a","xn--xkc2dl3a5ee0h","xn--y9a3aq","xn--yfro4i67o","xn--ygbi2ammx","xn--zfr164b","xperia","xxx","xyz","yachts","yahoo","yamaxun","yandex","ye","yodobashi","yoga","yokohama","you","youtube","yt","yun","za","zappos","zara","zero","zip","zippo","zm","zone","zuerich","zw"],a.htmlAttrs=["src=","data=","href=","cite=","formaction=","icon=","manifest=","poster=","codebase=","background=","profile=","usemap="]}),t=e(function(e,a){function t(e){var a=e.match(o);if(null===a)return!1;for(var t=r.length-1;t>=0;t--)if(r[t].test(e))return!1;var i=a[2];return!!i&&-1!==n.tlds.indexOf(i)}Object.defineProperty(a,"__esModule",{value:!0});var o=/^[a-z0-9!#$%&'*+\-\/=?^_`{|}~.]+@([a-z0-9%\-]+\.){1,}([a-z0-9\-]+)?$/i,r=[/^[!#$%&'*+\-\/=?^_`{|}~.]/,/[.]{2,}[a-z0-9!#$%&'*+\-\/=?^_`{|}~.]+@/i,/\.@/];a.default=t}),o=e(function(e,n){function t(e){if(!o.test(e))return!1;var n=e.split("."),t=Number(n[0]);if(isNaN(t)||t>255||t<0)return!1;var r=Number(n[1]);if(isNaN(r)||r>255||r<0)return!1;var i=Number(n[2]);if(isNaN(i)||i>255||i<0)return!1;var s=Number((n[3].match(/^\d+/)||[])[0]);if(isNaN(s)||s>255||s<0)return!1;var c=(n[3].match(/(^\d+)(:)(\d+)/)||[])[3];return!(c&&!a.isPort(c))}Object.defineProperty(n,"__esModule",{value:!0});var o=/^(\d{1,3}\.){3}\d{1,3}(:\d{1,5})?(\/([a-z0-9\-._~:\/\?#\[\]@!$&'\(\)\*\+,;=%]+)?)?$/i;n.default=t}),r=e(function(e,t){function o(e){var t=e.match(r);return null!==t&&("string"==typeof t[3]&&(-1!==n.tlds.indexOf(t[3].toLowerCase())&&!(t[5]&&!a.isPort(t[5]))))}Object.defineProperty(t,"__esModule",{value:!0});var r=/^(https?:\/\/|ftps?:\/\/)?([a-z0-9%\-]+\.){1,}([a-z0-9\-]+)?(:(\d{1,5}))?(\/([a-z0-9\-._~:\/\?#\[\]@!$&'\(\)\*\+,;=%]+)?)?$/i;t.default=o}),i=e(function(e,a){function n(e,a,t){return e.forEach(function(o,r){!(o.indexOf(".")>-1)||e[r-1]===a&&e[r+1]===t||e[r+1]!==a&&e[r+1]!==t||(e[r]=e[r]+e[r+1],"string"==typeof e[r+2]&&(e[r]=e[r]+e[r+2]),"string"==typeof e[r+3]&&(e[r]=e[r]+e[r+3]),"string"==typeof e[r+4]&&(e[r]=e[r]+e[r+4]),e.splice(r+1,4),n(e,a,t))}),e}function t(e){return e=n(e,"(",")"),e=n(e,"[","]"),e=n(e,'"','"'),e=n(e,"'","'")}Object.defineProperty(a,"__esModule",{value:!0}),a.fixSeparators=n,a.default=t}),s=e(function(e,a){function n(e){var a=e.replace(/([\s\(\)\[\]<>"'])/g,"\0$1\0").replace(/([?;:,.!]+)(?=(\0|$|\s))/g,"\0$1\0").split("\0");return i.default(a)}function t(e){return e.join("")}Object.defineProperty(a,"__esModule",{value:!0}),a.separate=n,a.deSeparate=t}),c=e(function(e,a){function n(e){return e=e.toLowerCase(),0===e.indexOf("http://")?"http://":0===e.indexOf("https://")?"https://":0===e.indexOf("ftp://")?"ftp://":0===e.indexOf("ftps://")?"ftps://":0===e.indexOf("file:///")?"file:///":0===e.indexOf("mailto:")&&"mailto:"}Object.defineProperty(a,"__esModule",{value:!0}),a.default=n}),l=e(function(e,a){function i(e,a){return e.map(function(i,s){var l=encodeURI(i);if(l.indexOf(".")<1&&!c.default(l))return i;var u=null,d=c.default(l)||"";return d&&(l=l.substr(d.length)),a.files&&"file:///"===d&&l.split(/\/|\\/).length-1&&(u={reason:"file",protocol:d,raw:i,encoded:l}),!u&&a.urls&&r.default(l)&&(u={reason:"url",protocol:d||("function"==typeof a.defaultProtocol?a.defaultProtocol(i):a.defaultProtocol),raw:i,encoded:l}),!u&&a.emails&&t.default(l)&&(u={reason:"email",protocol:"mailto:",raw:i,encoded:l}),!u&&a.ips&&o.default(l)&&(u={reason:"ip",protocol:d||("function"==typeof a.defaultProtocol?a.defaultProtocol(i):a.defaultProtocol),raw:i,encoded:l}),u&&("'"!==e[s-1]&&'"'!==e[s-1]||!~n.htmlAttrs.indexOf(e[s-2]))?u:i})}Object.defineProperty(a,"__esModule",{value:!0}),a.default=i}),u=e(function(e,a){function n(e,a){var n=o.separate(e),r=l.default(n,a);if(a.exclude)for(var i=0;i<r.length;i++){var c=r[i];"object"==typeof c&&a.exclude(c)&&(r[i]=c.raw)}if(a.list){for(var u=[],d=0;d<r.length;d++){var b=r[d];"string"!=typeof b&&u.push(b)}return u}return r=r.map(function(e){return"string"==typeof e?e:t(e,a)}),s.deSeparate(r)}function t(e,a){var n=e.protocol+e.encoded,t=e.raw;return"number"==typeof a.truncate&&t.length>a.truncate&&(t=t.substring(0,a.truncate)+"..."),"object"==typeof a.truncate&&t.length>a.truncate[0]+a.truncate[1]&&(t=t.substr(0,a.truncate[0])+"..."+t.substr(t.length-a.truncate[1])),void 0===a.attributes&&(a.attributes=[]),'<a href="'+n+'" '+a.attributes.map(function(a){if("function"!=typeof a)return" "+a.name+'="'+a.value+'" ';var n=(a(e)||{}).name,t=(a(e)||{}).value;return n&&!t?" name ":n&&t?" "+n+'="'+t+'" ':void 0}).join("")+">"+t+"</a>"}Object.defineProperty(a,"__esModule",{value:!0});var o=s;a.default=n}),d=e(function(e,n){Object.defineProperty(n,"__esModule",{value:!0});var i=function(e,n){return n=a.defaultOptions(n),u.default(e,n)};i.validate={ip:o.default,url:function(e){var a=c.default(e)||"";return e=e.substr(a.length),e=encodeURI(e),r.default(e)},email:t.default},n.default=i});return function(e){return e&&e.__esModule?e.default:e}(d)});
function verifyInputs(){
    var allPass = true;
    var message = "";
    $(".verify").each(function(){
        var thisPass = true;
        var input = $(this);
        var value;
        if(input.hasClass("editable")){
            value = tinyMCE.get(input.attr("id")).getContent();
            if(value.trim() === "" || ( value.indexOf("{{ default_title }}") > -1 ) || ( value.indexOf("{{ default_body }}") > -1 ) ){
                allPass = thisPass = false;
                input.addClass("error");
            }
            else if(input.data("limit-length") && value.length > 80 ){
                allPass = false;
                message += "Your petition title may not be longer than 80 characters.\n";
                input.addClass("error");
            }
        }
        else{
            value = input.val();
            if(value.length === 0){
                allPass = thisPass = false;
                input.addClass("error");
            }
        }
        if(!thisPass){
            var failMessage = input.data("verify-fail-message");
            message += failMessage + "\n";
        }
    });
    return allPass ? allPass : message;
}
function errorModal(message){
    window.errorModalInstance = new Modal({
        headerContent:"<h2>There is an error in your petition content.</h2>",
        bodyContent:message,
        iconContainerClass:"text-highlight",
        iconClass:"md-48",
        iconText:"error",
        bodyButtons: [
            ["Okay","material material-button minimal material-shadow margin-top margin-bottom transition","window.errorModalInstance.close()"]
        ]
    });
    errorModalInstance.open();
}
function unescape(string){
    /**
     * This function unescapes certain characters sent in the JSON response for each petition so they show up correctly.
     **/
    return string.replace(/\\"/g,"'")
        .replace(/\"/g,'')
        .replace(/&lt;/g,"<")
        .replace(/&gt;/g,">")
        .replace(/&amp;/g,"&")
        .replace(/nbps;/g," ")
        .replace(/"/g,"")
        .replace(/\\n/g, "\n")
        .replace(/(\\u201c|\\u201d)/g,'\"')
        .replace(/\\u2014/g,'&mdash;')
        .replace(/(\\u2019|\\u2018)/g,"'");
}
$(document).ready(function(){
    tinymce.init({
        selector: '#petition_description',
        inline: false,
        height: 230,
        menubar: false,
        plugins: "image link paste",
        branding: false,
        paste_auto_cleanup_on_paste : true,
        paste_remove_styles: true,
        paste_remove_styles_if_webkit: true,
        paste_strip_class_attributes: "all",
        paste_preprocess : function(pl, o) {
            o.content = anchorme(o.content);
        },
        toolbar: "insert | undo redo | styleselect | bold italic backcolor  | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link removeformat",
        init_instance_callback: function (editor) {
            editor.on('Change', function (e) {
                var value = e.level.content.trim();
                value = value.replace(/<\/?g[^>]*>/g, "");
                if(value !== ""){
                    update("description",value,petition_id);
                }
            });
        }
    });
    tinymce.init({
        selector: '#petition_title',
        inline: true,
        menubar: false,
        toolbar: false,
        init_instance_callback: function (editor) {
            editor.on('Change', function (e) {
                var value = ucfirst(e.level.content.trim().replace(/<\/?[^>]+(>|$)/g, ""));
                if(value.length > 80){
                    errorModal("Your petition title may not be longer than 80 characters.");
                }
                else{
                    if(value !== ""){
                        update("title",value,petition_id);
                    }
                }
            });
        }
    });

    $('#tags-select').select2({
        placeholder: "Petition Tags",
        width: "resolve",
        maximumSelectionLength: 3,
        noResults: function(){return "No tags found."},
        formatSelectionTooBig: "You can only select up to 3 tags."
    });
    var desc = $("#petition_description");
    var html = desc.html();
    desc.html(unescape(html));

});
var tags = $('#tags-select');
tags.on('select2:select', function (e) {
    var data = e.params.data;
    var id = data.id;
    update("add-tag",id,petition_id);
});
tags.on('select2:unselect', function (e) {
    var data = e.params.data;
    var id = data.id;
    update("remove-tag",id,petition_id);
});
$(document).on("click","#publish",function(){

    var verified = verifyInputs();
    if(verified === true){

        window.popup = new Modal({
            headerContent:"<h2>Are you sure you want to publish this petition?</h2>",
            bodyContent:"<p class='padding-bottom'>You cannot edit or delete it once it is published.</p>",
            iconContainerClass:"text-highlight",
            iconClass:"md-48",
            iconText:"warning",
            bodyButtons: [
                ["Cancel","material material-button minimal material-shadow margin-top margin-bottom transition","window.popup.close()"],
                ["Confirm", "material material-button material-shadow margin-bottom margin-top transition cursor","publishPetition("+petition_id+")"]
            ]
        });
        popup.open();

    }
    else{

        errorModal(verified);

    }

});