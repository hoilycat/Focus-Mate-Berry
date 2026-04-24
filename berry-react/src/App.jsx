import React, { useState, useEffect } from 'react';
import axios from 'axios';
// 필요한 아이콘들을 추가
import { Timer, User, Zap, Settings, X, Moon, Sun, Trophy, CheckCircle } from 'lucide-react';
//-------------베리가 태어나고 성장하는 이미지----------------------//
import imgSeed  from './images/seed.png';     // 씨앗 
import imgSprout  from './images/sprout.png'; // 새싹 
import imgSmall  from './images/small.png';   // 작은 열매 
import imgBig  from './images/big.png';       // 풍성한 열매

//------------베리가 다 성장 하고 나서 나오는 이미지-----------------//
import gifIdle   from './images/berryidle.gif'; // 평상시 
import berryCheer  from './images/cheerberry.gif';   // 응원하는 베리 로직에서 선언 해야함
import gifFinish   from './images/finishberry.gif';       // 완료 축하하는 베리
import gifSleep   from './images/sleepingberry.gif'; //  잠자는 베리
import gifStudy   from './images/study_berry2.gif';   // 공부하는 베리
import gifEating   from './images/eatingberry.gif';       // 군것질 하는 베리
import berryCall1  from './images/callingberry1.gif'; // 전화거는 베리1  로직에서 선언 해야함
import berryCall2  from './images/callingberry2.gif';   // 전화거는 베리2 로직에서 선언 해야함
import gifSick1   from './images/sickberry01.gif';       // 아픈 베리1 
import gifSick2   from './images/sickberry02.gif'; //  아파서 쓰러진 베리2_아픈 상태가 지속될 때 한번 나타나고 doom 상태로 이어짐
import gifDoom1   from './images/doomberry.gif'; // 굳어진 베리1 처음에 doom상태일때만 나타남
import gifDoom2   from './images/doomberry02.gif'; // 굳어진 베리2 doom상태가 지속될 때




function App() {
  // 1. 상태 관리 (데이터 및 설정)
  const [berry, setBerry] = useState(null);
  const [loading, setLoading] = useState(true);
  const [achievements, setAchievements] = useState([]); // 명예의 전당 데이터
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [isSparkling, setIsSparkling] = useState(false);//베리 상태가 초기화 될 때
  const [phonePhase, setPhonePhase] = useState(1); // 1단계 또는 2단계
  
  // 설정창용 입력값 상태
  const [inputName, setInputName] = useState("용용");
  const [inputGoal, setInputGoal] = useState(10);
  const [font, setFont] = useState("Nanum Gothic");

  // 2. 반짝임 효과 함수
  const triggerSparkle = () => {
    setIsSparkling(true);
    // 1.5초(1500) 뒤에 반짝이를 끄기
    setTimeout(() => {
      setIsSparkling(false);
    }, 1500);
  };


  // --- 2. 실시간 데이터 및 애니메이션 제어 ---

  // [A] 전화기 연기 로직
  useEffect(() => {
    if (berry?.status === "DOOM" || berry?.status?.includes("CALLING")) {
    setPhonePhase(1); // 일단 1단계로 시작!
    const timer = setTimeout(() => {
      setPhonePhase(2); // 2초 뒤에 2단계로 변신!
    }, 2000); 
    return () => clearTimeout(timer);
  } else {
    setPhonePhase(1); // 다른 상태일 땐 초기화
  }
}, [berry?.status]);

// [B] 실시간 데이터 연동 (상태 + 명예의 전당)
  useEffect(() => {
    const fetchData = async () => {
      try {
        // 현재 상태 가져오기
        const resStatus = await axios.get('http://localhost:8000/api/status');
        setBerry(resStatus.data);
        
        // 명예의 전당 가져오기
        const resAch = await axios.get('http://localhost:8000/api/achievements');
        setAchievements(resAch.data);

        // 처음 로딩 때만 서버에 저장된 이름을 입력창에 넣어줌
        if (loading) {
          setInputName(resStatus.data.user_name);
          setInputGoal(resStatus.data.goal_minutes);
        }
        setLoading(false);
      } catch (error) {
        console.error("서버 연결 대기 중...", error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, [loading]);

  // 명령 전송 함수
  const sendCommand = async (cmdText) => {
    try {
      await axios.post('http://localhost:8000/api/command', { cmd: cmdText });
      console.log(`명령 전송 성공: ${cmdText}`);
    } catch (error) {
      console.error("명령 전송 실패", error);
    }
  };

 // 3. 로딩 처리 (데이터가 없으면 여기서 멈춤)
  if (loading || !berry) return <div className="min-h-screen flex items-center justify-center bg-pink-50 text-pink-500 font-bold">베리 깨우는 중... 🍓</div>;
  
  
  // 4. 진행률 및 이모지 설정

  //진행률 계산 (사탕을 얼마나 먹었는지 계산)
  const goalSec = (berry?.goal_minutes || 10) * 60; // 목표 시간 (없으면 10분으로 생각!)
  const accSec = berry?.accumulated_time || 0;     // 공부한 시간 (없으면 0초!)
  const progress = (accSec / goalSec) * 100;       // 몇 퍼센트 했는지 계산!

  // 상태에 따른 이모지 매핑
  const getEmoji = (status) => {
    if (status.includes("SEED")) return "🌱";
    if (status.includes("SPROUT")) return "🌿";
    if (status.includes("SMALL")) return "🍓";
    if (status.includes("BIG")) return "🍎";
    if (status.includes("FAIRY")) return "✨";
    if (status === "EATING") return "😋";
    if (status === "SICK") return "🤒";
    if (status === "DOOM") return "💀";
    if (status === "FINISHED") return "🎉";
    return "💤";
  };

  // 5. 베리 이미지 및 효과 결정 함수

const getBerryAsset = (status, progress) => {
  let asset = gifIdle;
  let effectClass = "";

  // 👶 [1순위: 아기 검문소] 
  // 진행률이 76% 미만이면, 무조건 여기서 결정하고 끝낸다! (리턴)
  if (progress < 76) {
    // 1. 단계별 이미지 (씨앗, 새싹...)
    if (progress < 19) asset = imgSeed;
    else if (progress < 38) asset = imgSprout;
    else if (progress < 57) asset = imgSmall;
    else asset = imgBig;

    // 2. 아기용 효과 (흔들림, 필터)
    if (status === "SICK") {
      effectClass = "berry-sick-filter";
    } 
    else if (status.includes("DOOM") || status.includes("CALLING")) {
      effectClass = "berry-doom-shake"; 
    }
    else if (status === "SLEEP") {
      effectClass = "berry-sleep-opacity";
    }
    else if (status === "EATING") {
      effectClass = "grayscale brightness-125";
    }

    // 🚨 여기서 함수 종료! (밑에 어른 코드는 쳐다도 안 봄)
    return { asset, effectClass }; 
  }


 // 🧑 [2순위] 어른 단계 (76% 이상) - 리얼한 GIF 쇼!
  switch (status) {
    case "FINISHED":   asset = gifFinish; break;
    
    case "DOOM_STUCK": asset = gifDoom2; break; 
    case "CALLING_1":  asset = berryCall1; break; 
    case "CALLING_2":  asset = berryCall2; break; 
    case "DOOM": 
      asset = gifDoom1; 
      effectClass = "berry-doom-shake"; 
      break;

    case "SICK": asset = gifSick1; break;
    case "SICK_CRITICAL": asset = gifSick2; break;

    case "EATING": asset = gifEating; break;
    case "SLEEP":  asset = gifSleep; break;

    // 🚨 [여기를 수정했어!] 
    // GROWTH_FAIRY, GROWTH_BIG 등 이름이 뭐든 상관없이 'GROWTH'가 들어있으면 체크!
    default:
      if (status && status.includes("GROWTH")) {
        // 1. 키워드 대폭 추가! (최고, 멋져, 잘하고, 굿 등등)
        const cheerKeywords = ["파이팅", "힘내", "화이팅", "응원", "최고", "멋져", "잘하고", "굿", "Good", "🔥"];
        const isCheer = cheerKeywords.some(k => berry?.message?.includes(k));
        
        // 2. 키워드가 있으면 응원 베리, 아니면 공부 베리
        asset = isCheer ? berryCheer : gifStudy;
      } else {
        asset = gifIdle;
      }
      break;
  }

  return { asset, effectClass };
};


// 📍 [변수 계산] 화면을 그리기(return) 직전에 현재 베리의 모습과 효과를 가져오기
const { asset, effectClass } = getBerryAsset(berry.status, progress);


  return (
    // 다크모드 대응을 위해 최상단 div에 조건부 클래스 부여
    <div className={`${darkMode ? 'dark' : ''} transition-all duration-500`}>
      <div 
        className={`min-h-screen p-4 transition-all duration-500 ${darkMode ? 'bg-[#2D2424] text-pink-100' : 'bg-[#FFF0F5] text-gray-800'} ${berry.status.includes("WARNING") || berry.status.includes("주의") ? 'warning-active' : ''}`}
        style={{ fontFamily: font }} // 선택한 폰트 적용
      >
        {/* 구글 폰트 불러오기 */}
        <style>{`@import url('https://fonts.googleapis.com/css2?family=Gaegu&family=Nanum+Gothic:wght@400;700&family=Nanum+Pen+Script&display=swap');
        /* 🤒 아픈 베리: 흑백으로 변하고 약간 흐려짐 */
          .berry-sick-filter {
            filter: grayscale(100%) brightness(0.8) sepia(0.2);
            transition: all 0.5s ease;
          }

          /* 💀 위험한 베리: 덜덜덜 떨림! */
          .berry-doom-shake {
            animation: berry-shake 0.2s infinite;
            filter: saturate(2) contrast(1.5);
          }

          /* 💤 잠자는 베리: 투명해지고 흐릿해짐 */
          .berry-sleep-opacity {
            opacity: 0.5;
            filter: blur(2px);
            transition: all 1s ease;
          }

          @keyframes berry-shake {
            0% { transform: translate(1px, 1px); }
            50% { transform: translate(-1px, -2px); }
            100% { transform: translate(1px, 1px); }
          }
        
        /* ✨ 반짝반짝 가루 애니메이션 */
          .sparkle-particle {
            position: absolute;
            pointer-events: none;
            background: white;
            border-radius: 50%;
            animation: sparkle-fly 1s ease-out forwards;
            --x: attr(data-x);
            --y: attr(data-y);
          }

          @keyframes sparkle-fly {
            0% { transform: scale(0); opacity: 1; }
            100% { transform: scale(1.5) translate(var(--x), var(--y)); opacity: 0; }
          }

          /* 📞 전화 거는 둠 베리: 아주 어둡고 오싹한 느낌 */
          .berry-dark-face {
            filter: brightness(0.3) contrast(1.5) saturate(0.5);
            animation: berry-shake 0.1s infinite; /* 덜덜덜 떠는 효과 추가 */
            transition: all 0.3s ease;
          }

          /* 🚨 거북목 경고: 화면 가장자리가 주황색으로 깜빡임 */
          .warning-active {
            animation: warning-glow 1s infinite;
            box-shadow: inset 0 0 50px rgba(251, 191, 36, 0.4);
            border: 6px solid #FBBF24 !important;
          }

          @keyframes warning-glow {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; box-shadow: inset 0 0 100px rgba(251, 191, 36, 0.6); }
          }
        
        `}</style>

        {/* --- 상단 헤더 --- */}
        <header className={`max-w-md mx-auto flex items-center justify-between mb-8 pt-4 transition-all duration-300 ${berry.status.includes("WARNING") || berry.status.includes("주의") ? 'scale-110' : ''}`}>

          <h1 className={`text-2xl font-bold flex items-center gap-2 ${darkMode ? 'text-pink-300' : 'text-pink-500'}`}>
            <span>🍓</span> Focus Mate Berry
          </h1>
          <div className="flex gap-2">
            {/* 다크모드 토글 버튼 */}
            <button onClick={() => setDarkMode(!darkMode)} className="p-2 bg-white/50 dark:bg-black/20 rounded-full shadow-sm">
              {darkMode ? <Sun size={20} className="text-yellow-400"/> : <Moon size={20} className="text-pink-500"/>}
            </button>
            {/* 설정 사이드바 오픈 버튼 */}
            <button onClick={() => setIsSidebarOpen(true)} className="p-2 bg-white/50 dark:bg-black/20 rounded-full shadow-sm">
              <Settings size={20} className={darkMode ? "text-pink-300" : "text-pink-500"}/>
            </button>
          </div>
        </header>

        <main className="max-w-md mx-auto space-y-6">
          {/* --- 캐릭터 카드 섹션 --- */}
          <div className={`rounded-3xl p-8 shadow-xl transition-all duration-500 flex flex-col items-center ${darkMode ? 'bg-[#3D3232] border-pink-800 text-pink-200' : 'bg-white shadow-pink-100 border border-pink-50'}`}>
            {/* 말풍선 */}
            <div className={`relative p-4 rounded-2xl mb-6 text-center border-2 animate-bounce ${darkMode ? '!bg-[#4A3535] !border-pink-800 text-pink-200' : 'bg-pink-50 border-pink-100 text-pink-600'}`}>
              <p className="font-bold leading-relaxed">{berry.message}</p>
            <div className={`absolute -bottom-2 left-1/2 -translate-x-1/2 w-4 h-4 rotate-45 border-r-2 border-b-2 ${darkMode ? '!bg-[#4A3535] !border-pink-800' : 'bg-pink-50 border-pink-100'}`}></div>
            </div>

          {/* 캐릭터 이미지 (이모지 대신 불러온 GIF/PNG 적용) */}
          <div className={`w-48 h-48 rounded-full flex items-center justify-center mb-6 overflow-hidden transition-colors ${darkMode ? 'bg-pink-900/20' : 'bg-pink-50'}`}>
            <img 
              src={asset} 
              alt="Berry Animation" 
              className={`w-40 h-40 object-contain drop-shadow-xl ${effectClass}`}
              style={{ imageRendering: 'pixelated' }} 
            />

            {/* 💡 [추가!] 반짝이 가루 12개를 랜덤하게 뿌려요! */}
           {isSparkling && (
              <div className="absolute inset-0 pointer-events-none">
                {[...Array(12)].map((_, i) => {
                  const x = `${Math.random() * 200 - 100}px`;
                  const y = `${Math.random() * 200 - 100}px`;

                  return (
                    <div
                      key={i}
                      className="sparkle-particle"
                      data-x={x}
                      data-y={y}
                      style={{ left: "50%", top: "50%" }}
                    >
                      ✨
                    </div>
                  );
                })}
              </div>
            )}
          </div>

            {/* 진행바 */}
            <div className="w-full space-y-2">
              <div className="flex justify-between text-xs font-bold opacity-70">
                <span>PROGRESS</span>
                <span>{Math.min(Math.round(progress || 0), 100)}%</span>
              </div>
              <div className={`w-full h-4 rounded-full overflow-hidden ${darkMode ? 'bg-white/10' : 'bg-pink-100'}`}>
                <div 
                  className="h-full bg-gradient-to-r from-pink-400 to-pink-600 transition-all duration-1000 ease-out"
                  style={{ width: `${Math.min(progress, 100)}%` }}
                ></div>
              </div>
              <p className="text-center text-[10px] opacity-50">
                남은 시간: {Math.max(berry.goal_minutes - Math.floor(berry.accumulated_time / 60), 0)}분 / 목표: {berry.goal_minutes}분
              </p>
            </div>
          </div>

          {/* --- 하단 정보 그리드 --- */}
          <div className="grid grid-cols-2 gap-4">
            {/* --- 이름 정보 카드 --- */}
            <div className={`p-4 rounded-2xl shadow-sm border flex items-center gap-3 ${darkMode ? 'bg-[#3D3232] border-pink-900/30' : 'bg-white border-pink-50'}`}>
              <div className="bg-blue-50 dark:bg-blue-900/30 p-2 rounded-xl text-blue-500"><User size={20}/></div>
              <div>
                <p className="text-[10px] opacity-50">이름</p>
                <p className="font-bold text-sm">{berry.user_name}</p>
              </div>
            </div>

            {/* --- 상태 정보 카드 --- */}
            <div className={`p-4 rounded-2xl shadow-sm border flex items-center gap-3 ${darkMode ? 'bg-[#3D3232] border-pink-900/30' : 'bg-white border-pink-50'}`}>
              {/* 상태에 따라 아이콘 색상을 바꿉니다 */}
              <div className={`p-2 rounded-xl ${
                berry.status.includes("공부 중") ? "bg-green-50 text-green-500" : 
                berry.status.includes("주의") ? "bg-yellow-50 text-yellow-500" : 
                "bg-orange-50 text-orange-500"
              }`}>
                <Zap size={20}/>
              </div>
              <div>
                <p className="text-[10px] opacity-50">상태</p>
                {/* 텍스트가 길어질 수 있으므로 글자 크기를 살짝 조절 */}
                <p className="font-bold text-xs truncate w-32">{berry.status}</p>
              </div>
            </div>
          </div>

         {/* --- 컨트롤 버튼 섹션 --- */}
          <div className="flex gap-4">
           {/* --- 회복하기 버튼 (민트색 버전) --- */}
            <button 
              onClick={() => sendCommand("HEAL")}
              className={`flex-1 py-4 rounded-2xl font-bold transition-all duration-300
                active:scale-95 
                hover:scale-105 hover:brightness-110 hover:shadow-[0_0_15px_rgba(45,212,191,0.4)]
                ${darkMode 
                  ? '!bg-teal-900/50 !text-teal-200 !border-teal-500/50 border' // 다크모드: 차분한 진민트
                  : '!bg-teal-50 !text-teal-600 !border-teal-200 border'        // 라이트모드: 상큼한 연민트
                }`}
            >
              회복하기 💊
            </button>

            {/* 2. 시작/중단 변신 버튼 */}
            <button 
              onClick={() => berry?.is_running ? sendCommand("STOP") : sendCommand(`START|${inputName}|${inputGoal}`)}
              className={`flex-1 py-4 rounded-2xl font-bold !text-white shadow-lg transition-all duration-300
                active:scale-95
                hover:scale-105 hover:brightness-125 hover:shadow-pink-500/50 {/* 👈 더 반짝이는 효과! */}
                ${berry?.is_running 
                  ? '!bg-linear-to-r !from-red-400 !to-red-600' // 중단하기 버튼 (빨간색)
                  : '!bg-linear-to-r !from-pink-400 !to-pink-600' // 시작하기 버튼 (분홍색)
                }`}
            >
              {berry?.is_running ? '중단하기 ⏹️' : '시작하기 🚀'}
            </button>
          </div>

          {/* --- 🏆 명예의 전당 (추가된 기능) --- */}
          <div className={`p-6 rounded-3xl shadow-sm border ${darkMode ? 'bg-[#3D3232] border-pink-900/30' : 'bg-white border-pink-50'}`}>
            <h3 className="font-bold mb-4 flex items-center gap-2"><Trophy size={18} className="text-yellow-500"/> 명예의 전당</h3>
            <div className="space-y-3 max-h-40 overflow-y-auto pr-2">
              {achievements.length > 0 ? achievements.map((ach, idx) => (
                <div key={idx} className="flex justify-between items-center border-b border-pink-100/10 pb-2">
                  <div>
                    <p className="font-bold text-xs">{ach.user_name}</p>
                    <p className="text-[9px] opacity-40">{ach.completed_at}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-[10px] font-bold text-pink-500">{ach.goal_minutes}분 성공</p>
                    <p className="text-[9px] opacity-60">{getEmoji(ach.final_status)} {ach.final_status}</p>
                  </div>
                </div>
              )) : <p className="text-xs opacity-40 text-center py-4">아직 기록이 없어요!</p>}
            </div>
          </div>
        </main>

        {/* --- ⚙️ 설정 사이드바 (추가된 기능) --- */}
        <div className={`fixed inset-0 bg-black/50 z-50 transition-opacity duration-300 ${isSidebarOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
          <div className={`absolute right-0 top-0 h-full w-72 p-6 shadow-2xl transition-transform duration-300 ${darkMode ? 'bg-[#2D2424]' : 'bg-white'} ${isSidebarOpen ? 'translate-x-0' : 'translate-x-full'}`}>
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-xl font-bold flex items-center gap-2"><Settings size={20}/> 설정</h2>
              <button onClick={() => setIsSidebarOpen(false)} className="p-1"><X/></button>
            </div>
            <div className="space-y-6">
              <div>
                <label className="text-xs font-bold opacity-60 mb-2 block">내 이름</label>
                <input 
                  type="text" value={inputName} onChange={(e) => setInputName(e.target.value)}
                  className={`w-full p-3 rounded-xl border-2 outline-none ${darkMode ? 'bg-gray-800 border-pink-900 focus:border-pink-500' : 'bg-pink-50 border-pink-100 focus:border-pink-400'}`}
                />
              </div>
              <div>
                <label className="text-xs font-bold opacity-60 mb-2 block">목표 시간 (분)</label>
                <input 
                  type="number" value={inputGoal} onChange={(e) => setInputGoal(e.target.value)}
                  className={`w-full p-3 rounded-xl border-2 outline-none ${darkMode ? 'bg-gray-800 border-pink-900 focus:border-pink-500' : 'bg-pink-50 border-pink-100 focus:border-pink-400'}`}
                />
              </div>
              <div>
                <label className="text-xs font-bold opacity-60 mb-2 block">글꼴</label>
                <select value={font} onChange={(e) => setFont(e.target.value)}
                  className={`w-full p-3 rounded-xl border-2 ${darkMode ? 'bg-gray-800 border-pink-900' : 'bg-pink-50 border-pink-100'}`}>
                  <option value="Nanum Gothic">나눔 고딕</option>
                  <option value="Gaegu">개구체</option>
                  <option value="Nanum Pen Script">펜 글씨</option>
                </select>
              </div>
              <button 
                onClick={() => { sendCommand(`START|${inputName}|${inputGoal}`); setIsSidebarOpen(false); }}
                className="w-full py-4 bg-pink-500 text-white rounded-2xl font-bold shadow-lg active:scale-95"
              >
                적용 후 시작 🍓
              </button>

              {/*--새로 시작 버튼--*/}
              <div className="mt-8 pt-6 border-t border-gray-100">
              <p className="text-sm text-gray-400 mb-3">베리의 기억을 지우고 새로 시작할래?</p>
              
              <button 
                onClick={() => {
                  if(window.confirm("정말 처음부터 다시 키울 거야? 베리가 아기가 될 텐데! 🥺")) {
                    sendCommand("RESET");
                    triggerSparkle(); // 반짝임 효과 발동
                  }
                }}
                className="w-full py-4 rounded-2xl font-bold bg-gray-100 text-gray-500 hover:bg-red-50 hover:text-red-500 transition-all border-none outline-none shadow-sm"
              >
                처음부터 다시 키우기 🔄
              </button>
            </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;