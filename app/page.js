"use client";

import { useEffect, useMemo, useState } from "react";

const stages = [
  { name: "씨앗", level: 1, need: 0, image: "/seed.png", icon: "🌱", note: "새로운 배움의 시작" },
  { name: "새싹", level: 2, need: 2, image: "/sprout.png", icon: "🌿", note: "작은 습관이 자라는 중" },
  { name: "본잎", level: 3, need: 6, image: "/leaves.png", icon: "🍃", note: "배움의 뿌리가 단단해져요" },
  { name: "꽃", level: 4, need: 12, image: "/flower-v2.png", icon: "🌸", note: "노력이 멋지게 피어났어요" },
  { name: "열매", level: 5, need: 20, image: "/fruit-v2.png", icon: "🍎", note: "배움이 값진 결실이 되었어요" }
];

// 직접 바꿀 수 있는 기본 보유 비료 개수입니다.
const INITIAL_FERTILIZER_STOCK = 100;
const FERTILIZER_STOCK_VERSION = "100-v2";
const CHUNCHEON_DISTRICTS = [
  "신북읍", "동면", "동산면", "신동면", "동내면", "남면", "남산면", "서면", "사북면", "북산면",
  "소양동", "교동", "조운동", "약사명동", "근화동", "후평1동", "후평2동", "후평3동",
  "효자1동", "효자2동", "효자3동", "석사동", "퇴계동", "강남동", "신사우동"
];

function stageFor(fertilizer) {
  return stages.reduce((found, stage, index) => fertilizer >= stage.need ? index : found, 0);
}

function programFields(program) {
  return [
    ...(program.is_sw === "1" ? ["is_sw"] : []),
    ...(program.is_ai === "1" ? ["is_ai"] : []),
    ...(program.is_bio === "1" ? ["is_bio"] : []),
  ];
}

function programCategories(program) {
  return programFields(program).map((field) => ({
    is_sw: "SW",
    is_ai: "AI",
    is_bio: "바이오",
  })[field]);
}

const FEATURED_CATEGORIES = [
  { name: "SW", fields: ["is_sw"] },
  { name: "AI", fields: ["is_ai"] },
  { name: "바이오", fields: ["is_bio"] },
  { name: "AI·SW 융합", fields: ["is_ai", "is_sw"] },
  { name: "AI·바이오 융합", fields: ["is_ai", "is_bio"] },
  { name: "SW·바이오 융합", fields: ["is_sw", "is_bio"] },
  { name: "AI·SW·바이오 융합", fields: ["is_ai", "is_sw", "is_bio"] },
];

function isFeaturedCategory(program, fields) {
  const fieldsForProgram = programFields(program);
  return ["is_sw", "is_ai", "is_bio"].every((field) => (
    fields.includes(field) ? fieldsForProgram.includes(field) : !fieldsForProgram.includes(field)
  ));
}

function randomProgramOrder(program) {
  return String(program.program_id).split("").reduce(
    (value, character) => ((value * 31) + character.charCodeAt(0)) >>> 0,
    2166136261
  );
}

function ProgramCard({ program, onApply }) {
  const categories = programCategories(program);
  return (
    <article className="program-card">
      <div className="program-card-top">
        <div className="program-category-tags">
          {categories.map((category) => <span className={category.toLowerCase()} key={category}>{category}</span>)}
        </div>
        <span className={`program-status ${program.status_label === "진행중" ? "ongoing" : ""}`}>{program.status_label || "일정 확인"}</span>
      </div>
      <h3>{program.title}</h3>
      <p className="program-provider">{program.provider || "제공 기관 확인"}</p>
      <p className="program-summary">{program.summary || "프로그램 상세 페이지에서 교육 내용을 확인해보세요."}</p>
      <dl>
        <div><dt>대상</dt><dd>{program.grade_label || "대상 확인"}</dd></div>
        <div><dt>기간</dt><dd>{program.start_date && program.end_date ? `${program.start_date} ~ ${program.end_date}` : "일정 확인"}</dd></div>
        <div><dt>장소</dt><dd>{program.is_online === "1" ? "온라인" : program.place_name || "장소 확인"}</dd></div>
      </dl>
      <button className="program-apply" onClick={() => onApply(program)}>신청하기 <span>→</span></button>
    </article>
  );
}

export default function Home() {
  const [profile, setProfile] = useState(null);
  const [showStudentLogin, setShowStudentLogin] = useState(false);
  const [teacherNotice, setTeacherNotice] = useState(false);
  const [programs, setPrograms] = useState([]);
  const [programLoading, setProgramLoading] = useState(true);
  const [programError, setProgramError] = useState("");
  const [programCategory, setProgramCategory] = useState("전체보기");
  const [featuredCategory, setFeaturedCategory] = useState("AI");
  const [visibleProgramCount, setVisibleProgramCount] = useState(12);
  const [studentPage, setStudentPage] = useState("programs");
  const [pendingProgram, setPendingProgram] = useState(null);
  const [profileForm, setProfileForm] = useState(null);
  const [profileSaving, setProfileSaving] = useState(false);
  const [profileSaveMessage, setProfileSaveMessage] = useState("");
  const [loginId, setLoginId] = useState("");
  const [loginPassword, setLoginPassword] = useState("");
  const [joinMode, setJoinMode] = useState("existing");
  const [profileLoading, setProfileLoading] = useState(false);
  const [profileError, setProfileError] = useState("");
  const [joinForm, setJoinForm] = useState({
    login_id: "",
    login_password: "",
    login_password_confirm: "",
    stu_name: "",
    gender: "",
    school_level: "",
    grade: "",
    district_name: "",
    interest_category: ""
  });
  const [fertilizer, setFertilizer] = useState(0);
  const [fertilizerStock, setFertilizerStock] = useState(INITIAL_FERTILIZER_STOCK);
  const [harvestedFruits, setHarvestedFruits] = useState(0);
  const [fruitType, setFruitType] = useState("apple");
  const [isFeeding, setIsFeeding] = useState(false);
  const [celebrate, setCelebrate] = useState(false);
  const currentIndex = stageFor(fertilizer);
  const displayStages = useMemo(() => stages.map((stage, index) => {
    if (index === 3) {
      return { ...stage, image: fruitType === "orange" ? "/flower-orange-v1.png" : "/flower-v2.png" };
    }
    if (index === 4) {
      return {
        ...stage,
        image: fruitType === "orange" ? "/fruit-orange-v1.png" : "/fruit-v2.png",
        icon: fruitType === "orange" ? "🍊" : "🍎"
      };
    }
    return stage;
  }), [fruitType]);
  const current = displayStages[currentIndex];
  const next = displayStages[currentIndex + 1];
  const filteredPrograms = useMemo(
    () => programs.filter((program) => (
      programCategory === "전체보기" || programCategories(program).includes(programCategory)
    )),
    [programs, programCategory]
  );
  const featuredPrograms = useMemo(() => {
    const recruiting = programs.filter((program) => program.status_label === "모집중");
    return FEATURED_CATEGORIES.map(({ name, fields }) => ({
      category: name,
      programs: recruiting
        .filter((program) => isFeaturedCategory(program, fields))
        .map((program) => ({ program, order: randomProgramOrder(program) }))
        .sort((a, b) => a.order - b.order)
        .slice(0, 3)
        .map(({ program }) => program),
    }));
  }, [programs]);

  const progress = useMemo(() => {
    if (!next) return 100;
    return ((fertilizer - current.need) / (next.need - current.need)) * 100;
  }, [fertilizer, current, next]);

  useEffect(() => {
    fetch("/api/programs")
      .then((response) => {
        if (!response.ok) throw new Error("프로그램 정보를 불러오지 못했습니다.");
        return response.json();
      })
      .then((data) => setPrograms(data.programs || []))
      .catch((error) => setProgramError(error.message))
      .finally(() => setProgramLoading(false));

    const saved = Number(localStorage.getItem("growth-fertilizer"));
    const savedStockValue = localStorage.getItem("growth-fertilizer-stock");
    const savedStock = Number(savedStockValue);
    const savedFruits = Number(localStorage.getItem("growth-harvested-fruits"));
    const savedFruitType = localStorage.getItem("growth-current-fruit");
    const stockVersion = localStorage.getItem("growth-stock-version");
    if (Number.isFinite(saved) && saved >= 0 && saved <= 20) setFertilizer(saved);
    if (stockVersion !== FERTILIZER_STOCK_VERSION) {
      setFertilizerStock(INITIAL_FERTILIZER_STOCK);
      localStorage.setItem("growth-fertilizer-stock", String(INITIAL_FERTILIZER_STOCK));
      localStorage.setItem("growth-stock-version", FERTILIZER_STOCK_VERSION);
    } else if (savedStockValue !== null && Number.isFinite(savedStock) && savedStock >= 0) {
      setFertilizerStock(savedStock);
    }
    if (Number.isFinite(savedFruits) && savedFruits >= 0) setHarvestedFruits(savedFruits);
    setFruitType(
      savedFruitType === "apple" || savedFruitType === "orange"
        ? savedFruitType
        : savedFruits % 2 === 1 ? "orange" : "apple"
    );
  }, []);

  function enterAsStudent(student, isNew = false) {
    setProfile(student);
    setProfileForm({ ...student });
    setStudentPage("programs");
    localStorage.setItem("growth-profile", JSON.stringify(student));
    if (isNew) {
      setFertilizer(0);
      setFertilizerStock(0);
      setHarvestedFruits(0);
      setFruitType("apple");
      localStorage.setItem("growth-fertilizer", "0");
      localStorage.setItem("growth-fertilizer-stock", "0");
      localStorage.setItem("growth-harvested-fruits", "0");
      localStorage.setItem("growth-current-fruit", "apple");
      localStorage.setItem("growth-stock-version", FERTILIZER_STOCK_VERSION);
      return;
    }
    const stageIndex = Math.max(0, stages.findIndex((stage) => stage.name === student.growth_stage));
    setFertilizer(stages[stageIndex].need);
    setFertilizerStock(Number(student.fertilizer_count) || 0);
    localStorage.setItem("growth-fertilizer", String(stages[stageIndex].need));
    localStorage.setItem("growth-fertilizer-stock", String(Number(student.fertilizer_count) || 0));
  }

  async function selectExistingStudent(event) {
    event.preventDefault();
    if (!loginId.trim() || !loginPassword) {
      setProfileError("아이디와 비밀번호를 모두 입력해주세요.");
      return;
    }
    setProfileLoading(true);
    setProfileError("");
    try {
      const response = await fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ login_id: loginId, login_password: loginPassword })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "로그인하지 못했습니다.");
      enterAsStudent(data.student);
    } catch (error) {
      setProfileError(error.message);
    } finally {
      setProfileLoading(false);
    }
  }

  async function registerStudent(event) {
    event.preventDefault();
    if (profileLoading) return;
    if (joinForm.login_password !== joinForm.login_password_confirm) {
      setProfileError("비밀번호 확인이 일치하지 않습니다.");
      return;
    }
    setProfileLoading(true);
    setProfileError("");
    try {
      const response = await fetch("/api/students", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(joinForm)
      });
      const data = await response.json().catch(() => {
        throw new Error("가입 서버에 연결되지 않았습니다. http://127.0.0.1:8080 주소인지 확인해주세요.");
      });
      if (!response.ok) throw new Error(data.error || "학생 정보를 저장하지 못했습니다.");
      window.history.replaceState(null, "", "#garden");
      enterAsStudent(data.student, true);
      requestAnimationFrame(() => window.scrollTo({ top: 0, behavior: "auto" }));
    } catch (error) {
      setProfileError(error.message);
    } finally {
      setProfileLoading(false);
    }
  }

  function changeStudent() {
    localStorage.removeItem("growth-profile");
    setLoginId("");
    setLoginPassword("");
    setProfileError("");
    setProfile(null);
    setShowStudentLogin(false);
    setStudentPage("programs");
    setProfileForm(null);
    setPendingProgram(null);
  }

  function openStudentLogin() {
    setPendingProgram(null);
    setShowStudentLogin(true);
    requestAnimationFrame(() => window.scrollTo({ top: 0, behavior: "auto" }));
  }

  function applyForProgram(program) {
    if (!profile) {
      setPendingProgram(program);
      setShowStudentLogin(true);
      requestAnimationFrame(() => window.scrollTo({ top: 0, behavior: "auto" }));
      return;
    }
    if (program.detail_url) {
      window.open(program.detail_url, "_blank", "noopener,noreferrer");
      setPendingProgram(null);
    }
  }

  async function saveProfile(event) {
    event.preventDefault();
    setProfileSaving(true);
    setProfileSaveMessage("");
    try {
      const response = await fetch("/api/students/update", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(profileForm),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "학생 정보를 수정하지 못했습니다.");
      setProfile(data.student);
      setProfileForm({ ...data.student });
      localStorage.setItem("growth-profile", JSON.stringify(data.student));
      setProfileSaveMessage("기본 정보가 저장되었습니다.");
    } catch (error) {
      setProfileSaveMessage(error.message);
    } finally {
      setProfileSaving(false);
    }
  }

  function feed() {
    if (isFeeding || fertilizer >= 20 || fertilizerStock <= 0) return;
    setIsFeeding(true);
    const before = stageFor(fertilizer);
    const updated = Math.min(20, fertilizer + 1);
    setTimeout(() => {
      setFertilizer(updated);
      setFertilizerStock((stock) => {
        const remaining = Math.max(0, stock - 1);
        localStorage.setItem("growth-fertilizer-stock", String(remaining));
        return remaining;
      });
      localStorage.setItem("growth-fertilizer", String(updated));
      if (stageFor(updated) > before) {
        setCelebrate(true);
        if (updated === 20) {
          setHarvestedFruits((fruits) => {
            const total = fruits + 1;
            localStorage.setItem("growth-harvested-fruits", String(total));
            return total;
          });
          setTimeout(() => {
            setCelebrate(false);
            setFertilizer(0);
            const nextFruitType = fruitType === "apple" ? "orange" : "apple";
            setFruitType(nextFruitType);
            localStorage.setItem("growth-fertilizer", "0");
            localStorage.setItem("growth-current-fruit", nextFruitType);
          }, 3500);
        } else {
          setTimeout(() => setCelebrate(false), 3500);
        }
      }
      setIsFeeding(false);
    }, 900);
  }

  function reset() {
    setFertilizer(0);
    setFertilizerStock(INITIAL_FERTILIZER_STOCK);
    setHarvestedFruits(0);
    setFruitType("apple");
    localStorage.setItem("growth-fertilizer", "0");
    localStorage.setItem("growth-fertilizer-stock", String(INITIAL_FERTILIZER_STOCK));
    localStorage.setItem("growth-harvested-fruits", "0");
    localStorage.setItem("growth-current-fruit", "apple");
    localStorage.setItem("growth-stock-version", FERTILIZER_STOCK_VERSION);
    setCelebrate(false);
  }

  if ((!profile && !showStudentLogin) || (profile && studentPage === "programs")) {
    const isStudentCatalog = Boolean(profile);
    return (
      <main className="program-page">
        <header className="program-header">
          <a className="program-brand" href="#" aria-label="봄내틔움 프로그램 홈">
            <img src="/bomnae-logo-transparent-v3.png" alt="봄내틔움" />
          </a>
          {isStudentCatalog ? (
            <>
              <nav className="student-main-nav" aria-label="학생 주요 메뉴">
                <button className="active" onClick={() => setStudentPage("programs")}>프로그램 신청</button>
                <button onClick={() => setStudentPage("garden")}>성장 정원</button>
                <button onClick={() => setStudentPage("mypage")}>마이페이지</button>
              </nav>
              <nav className="program-login-actions" aria-label="학생 계정">
                <span className="student-welcome"><b>{profile.stu_name}</b> 학생</span>
                <button className="student-login-button" onClick={changeStudent}>로그아웃</button>
              </nav>
            </>
          ) : (
            <nav className="program-login-actions" aria-label="로그인">
              <button className="student-login-button" onClick={openStudentLogin}>학생 로그인</button>
              <button className="teacher-login-button" onClick={() => setTeacherNotice(true)}>선생님 로그인</button>
            </nav>
          )}
        </header>

        <section className="program-hero">
          <div className="program-hero-copy">
            <img src="/main_left.png" alt="춘천 청소년의 배움이 열매 맺는 곳, 봄내틔움" />
          </div>
          <div className="program-hero-art">
            <img src="/main_right.png" alt="" />
          </div>
        </section>

        <section className="program-catalog">
          <div className="program-section-heading">
            <div>
              <span>PROGRAMS</span>
              <h2>{isStudentCatalog ? "전체 배움 프로그램" : "지금 인기 있는 프로그램"}</h2>
              <p>{isStudentCatalog ? "관심 분야를 선택해 프로그램을 찾아보세요." : "현재 신청 가능한 프로그램을 분야별로 추천해드려요."}</p>
            </div>
            {isStudentCatalog && <strong>총 {filteredPrograms.length}개</strong>}
          </div>

          {programLoading ? (
            <div className="program-state">프로그램을 불러오는 중이에요…</div>
          ) : programError ? (
            <div className="program-state error">{programError}</div>
          ) : !isStudentCatalog ? (
            <div className="featured-program-sections">
              <div className="featured-category-tabs">
                {FEATURED_CATEGORIES.map(({ name: category }) => (
                  <button
                    className={featuredCategory === category ? "active" : ""}
                    key={category}
                    onClick={() => setFeaturedCategory(category)}
                  >
                    {category}
                  </button>
                ))}
              </div>
              {featuredPrograms
                .filter(({ category }) => category === featuredCategory)
                .map(({ category, programs: categoryPrograms }) => (
                  <section className="featured-program-group" key={category}>
                    <div className="featured-program-title">
                      <span>{category}</span>
                      <h3>{category} 인기 프로그램</h3>
                    </div>
                    <div className="program-grid">
                      {categoryPrograms.length ? (
                        categoryPrograms.map((program) => <ProgramCard program={program} onApply={applyForProgram} key={program.program_id} />)
                      ) : (
                        <p className="program-state">현재 모집 중인 프로그램이 없습니다.</p>
                      )}
                    </div>
                  </section>
                ))}
            </div>
          ) : (
            <>
              {pendingProgram && (
                <div className="pending-application">
                  <div><span>선택한 프로그램</span><b>{pendingProgram.title}</b></div>
                  <button onClick={() => applyForProgram(pendingProgram)}>신청 계속하기 →</button>
                </div>
              )}
              <div className="program-filters">
                {["전체보기", "SW", "AI", "바이오"].map((category) => (
                  <button
                    className={programCategory === category ? "active" : ""}
                    key={category}
                    onClick={() => {
                      setProgramCategory(category);
                      setVisibleProgramCount(12);
                    }}
                  >
                    {category}
                  </button>
                ))}
              </div>
              <div className="program-grid">
                {filteredPrograms.slice(0, visibleProgramCount).map((program) => <ProgramCard program={program} onApply={applyForProgram} key={program.program_id} />)}
              </div>
              {visibleProgramCount < filteredPrograms.length && (
                <button className="program-more" onClick={() => setVisibleProgramCount((count) => count + 12)}>프로그램 더 보기</button>
              )}
            </>
          )}
        </section>

        {teacherNotice && (
          <div className="teacher-notice-backdrop" onClick={() => setTeacherNotice(false)}>
            <div className="teacher-notice" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}>
              <span>👩‍🏫</span>
              <h2>선생님 로그인</h2>
              <p>선생님 계정 기능은 현재 준비 중입니다.</p>
              <button onClick={() => setTeacherNotice(false)}>확인</button>
            </div>
          </div>
        )}
      </main>
    );
  }

  if (!profile) {
    const maxGrade = joinForm.school_level === "초등학교" ? 6 : 3;
    return (
      <main className="onboarding-page">
        <button className="login-back-button" onClick={() => { setShowStudentLogin(false); setPendingProgram(null); }}>← 프로그램으로 돌아가기</button>
        <div className="onboarding-decoration deco-one">✦</div>
        <div className="onboarding-decoration deco-two">🌿</div>
        <section className="onboarding-card">
          <div className="onboarding-showcase">
            <img
              className="login-hero-image"
              src="/log_in.png"
              alt="봄내틔움 학생 성장 서비스"
            />
          </div>
          <div className="onboarding-content">
            <div className="onboarding-content-heading">
              <span>{joinMode === "existing" ? "다시 만나 반가워요" : "나의 씨앗 만들기"}</span>
              <h1>{joinMode === "existing" ? "나의 성장 정원" : "학생 정보 등록"}</h1>
              <p>{joinMode === "existing" ? "가입한 아이디와 비밀번호로 로그인하세요." : "로그인 정보와 학생 기본 정보를 입력해주세요."}</p>
            </div>
            <div className="join-tabs">
              <button className={joinMode === "existing" ? "active" : ""} onClick={() => setJoinMode("existing")}>기존 학생</button>
              <button className={joinMode === "new" ? "active" : ""} onClick={() => setJoinMode("new")}>신규 가입</button>
            </div>

            {joinMode === "existing" ? (
              <form className="existing-student-panel" onSubmit={selectExistingStudent}>
              <label>
                <span>아이디</span>
                <input value={loginId} onChange={(event) => setLoginId(event.target.value)} placeholder="아이디를 입력해주세요" autoComplete="username" disabled={profileLoading} />
              </label>
              <label>
                <span>비밀번호</span>
                <input type="password" value={loginPassword} onChange={(event) => setLoginPassword(event.target.value)} placeholder="비밀번호를 입력해주세요" autoComplete="current-password" disabled={profileLoading} />
              </label>
              <div className="selected-preview">
                <span>🌱</span>
                <p><b>가입할 때 설정한 아이디와 비밀번호를 입력해주세요.</b>로그인 정보는 개인정보 보호를 위해 화면에 표시하지 않습니다.</p>
              </div>
              <button className="join-submit" type="submit" disabled={profileLoading}>{profileLoading ? "로그인 중…" : "로그인"}</button>
              </form>
            ) : (
              <form className="join-form" onSubmit={registerStudent}>
              <label className="full-field">
                <span>아이디</span>
                <input value={joinForm.login_id} onChange={(event) => setJoinForm({ ...joinForm, login_id: event.target.value })} placeholder="영문, 숫자, 밑줄 4~20자" autoComplete="username" minLength="4" maxLength="20" pattern="[A-Za-z0-9_]+" required />
              </label>
              <label>
                <span>비밀번호</span>
                <input type="password" value={joinForm.login_password} onChange={(event) => setJoinForm({ ...joinForm, login_password: event.target.value })} placeholder="6자 이상 입력" autoComplete="new-password" minLength="6" required />
              </label>
              <label>
                <span>비밀번호 확인</span>
                <input type="password" value={joinForm.login_password_confirm} onChange={(event) => setJoinForm({ ...joinForm, login_password_confirm: event.target.value })} placeholder="비밀번호 다시 입력" autoComplete="new-password" minLength="6" required />
              </label>
              <label className="full-field">
                <span>이름</span>
                <input value={joinForm.stu_name} onChange={(event) => setJoinForm({ ...joinForm, stu_name: event.target.value })} placeholder="이름을 입력하세요" required />
              </label>
              <label>
                <span>성별</span>
                <select value={joinForm.gender} onChange={(event) => setJoinForm({ ...joinForm, gender: event.target.value })} required>
                  <option value="">선택</option><option value="남">남</option><option value="여">여</option>
                </select>
              </label>
              <label>
                <span>학년</span>
                <div className="grade-selects">
                  <select value={joinForm.school_level} onChange={(event) => setJoinForm({ ...joinForm, school_level: event.target.value, grade: "" })} required>
                    <option value="">학교급</option><option value="초등학교">초등학교</option><option value="중학교">중학교</option><option value="고등학교">고등학교</option>
                  </select>
                  <select value={joinForm.grade} onChange={(event) => setJoinForm({ ...joinForm, grade: event.target.value })} required disabled={!joinForm.school_level}>
                    <option value="">학년</option>
                    {Array.from({ length: maxGrade }, (_, index) => <option value={index + 1} key={index + 1}>{index + 1}학년</option>)}
                  </select>
                </div>
              </label>
              <label>
                <span>사는 지역</span>
                <select value={joinForm.district_name} onChange={(event) => setJoinForm({ ...joinForm, district_name: event.target.value })} required>
                  <option value="">지역 선택</option>
                  {CHUNCHEON_DISTRICTS.map((district) => <option value={district} key={district}>{district}</option>)}
                </select>
              </label>
              <label>
                <span>관심사</span>
                <select value={joinForm.interest_category} onChange={(event) => setJoinForm({ ...joinForm, interest_category: event.target.value })} required>
                  <option value="">관심 분야 선택</option><option value="AI">AI</option><option value="SW">SW</option><option value="바이오">바이오</option>
                </select>
              </label>
              <div className="new-student-notice full-field"><span>🌱</span><p><b>신규 학생은 씨앗 단계에서 시작해요.</b>보유 비료 0개로 등록되며 활동을 통해 비료를 모을 수 있어요.</p></div>
              <button className="join-submit full-field" type="submit" disabled={profileLoading}>
                {profileLoading ? "성장 씨앗을 만드는 중…" : "내 성장 씨앗 만들기"}
              </button>
              </form>
            )}
            {profileError && <p className="profile-error">{profileError}</p>}
          </div>
        </section>
      </main>
    );
  }

  if (studentPage === "mypage") {
    const profileMaxGrade = profileForm?.school_level === "초등학교" ? 6 : 3;
    const profileGrade = String(profileForm?.grade || "").replace(/^[emh]/, "");
    return (
      <main className="mypage-page">
        <header className="program-header">
          <a className="program-brand" href="#" onClick={(event) => { event.preventDefault(); setStudentPage("programs"); }}>
            <img src="/bomnae-logo-transparent-v3.png" alt="봄내틔움" />
          </a>
          <nav className="student-main-nav" aria-label="학생 주요 메뉴">
            <button onClick={() => setStudentPage("programs")}>프로그램 신청</button>
            <button onClick={() => setStudentPage("garden")}>성장 정원</button>
            <button className="active">마이페이지</button>
          </nav>
          <nav className="program-login-actions" aria-label="학생 계정">
            <span className="student-welcome"><b>{profile.stu_name}</b> 학생</span>
            <button className="student-login-button" onClick={changeStudent}>로그아웃</button>
          </nav>
        </header>

        <section className="mypage-hero">
          <span>MY PAGE</span>
          <h1>{profile.stu_name}님의 마이페이지</h1>
          <p>내 정보를 관리하고 성장 정원을 확인할 수 있어요.</p>
        </section>

        <section className="mypage-layout">
          <aside className="mypage-profile-card">
            <div className="mypage-avatar">{profile.stu_name?.slice(0, 1)}</div>
            <span>MY PROFILE</span>
            <h2>{profile.stu_name}</h2>
            <p>{profile.stu_id}</p>
            <dl>
              <div><dt>학년</dt><dd>{profile.school_level} {profile.grade}</dd></div>
              <div><dt>사는 지역</dt><dd>{profile.district_name}</dd></div>
              <div><dt>관심 분야</dt><dd>{profile.interest_category}</dd></div>
            </dl>
          </aside>

          <div className="mypage-content">
            <form className="profile-edit-form" onSubmit={saveProfile}>
              <div className="profile-form-heading">
                <span>PROFILE INFORMATION</span>
                <h2>기본 정보 수정</h2>
                <p>변경할 정보를 입력한 뒤 저장해주세요.</p>
              </div>
              <label>
                <span>이름</span>
                <input value={profileForm?.stu_name || ""} onChange={(event) => setProfileForm({ ...profileForm, stu_name: event.target.value })} required />
              </label>
              <label>
                <span>성별</span>
                <select value={profileForm?.gender || ""} onChange={(event) => setProfileForm({ ...profileForm, gender: event.target.value })} required>
                  <option value="남">남</option><option value="여">여</option>
                </select>
              </label>
              <label>
                <span>학교급</span>
                <select value={profileForm?.school_level || ""} onChange={(event) => setProfileForm({ ...profileForm, school_level: event.target.value, grade: "" })} required>
                  <option value="초등학교">초등학교</option><option value="중학교">중학교</option><option value="고등학교">고등학교</option>
                </select>
              </label>
              <label>
                <span>학년</span>
                <select value={profileGrade} onChange={(event) => setProfileForm({ ...profileForm, grade: event.target.value })} required>
                  <option value="">학년 선택</option>
                  {Array.from({ length: profileMaxGrade }, (_, index) => <option value={String(index + 1)} key={index + 1}>{index + 1}학년</option>)}
                </select>
              </label>
              <label>
                <span>사는 지역</span>
                <select value={profileForm?.district_name || ""} onChange={(event) => setProfileForm({ ...profileForm, district_name: event.target.value })} required>
                  {CHUNCHEON_DISTRICTS.map((district) => <option value={district} key={district}>{district}</option>)}
                </select>
              </label>
              <label>
                <span>관심 분야</span>
                <select value={profileForm?.interest_category || ""} onChange={(event) => setProfileForm({ ...profileForm, interest_category: event.target.value })} required>
                  <option value="SW">SW</option><option value="AI">AI</option><option value="바이오">바이오</option>
                </select>
              </label>
              {profileSaveMessage && <p className="profile-save-message">{profileSaveMessage}</p>}
              <button className="profile-save-button" type="submit" disabled={profileSaving}>{profileSaving ? "저장 중…" : "변경사항 저장"}</button>
            </form>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main className="page-shell">
      <nav className="topbar">
        <a className="brand" href="#garden" aria-label="성장 정원 처음으로">
          <img src="/bomnae-logo-transparent-v3.png" alt="봄내티움" />
        </a>
        <div className="nav-links">
          <button onClick={() => setStudentPage("programs")}>프로그램 신청</button>
          <button className="active">성장 정원</button>
          <button onClick={() => setStudentPage("mypage")}>마이페이지</button>
        </div>
        <div className="header-profile"><span>{profile.stu_name?.slice(0, 1)}</span><p><b>{profile.stu_name}</b><small>{profile.school_level} {profile.grade}학년</small></p></div>
      </nav>

      <section className="hero" id="garden">
        <div className="hero-copy">
          <div className="eyebrow">BOMNAE-TIUM STUDENT SERVICE</div>
          <h1><em>{profile.stu_name}</em>님의 배움이<br />오늘도 자라고 있어요.</h1>
          <p>작은 활동 하나가 비료가 되고, 꾸준한 배움은 멋진 열매가 됩니다.</p>
        </div>
        <div className="welcome-card"><span>{current.icon}</span><p><b>현재 {current.name} 단계</b>다음 단계까지 비료 {next ? next.need - fertilizer : 0}개가 남았어요.</p></div>
      </section>

      <section className="garden-card">
        <div className="stage-meta">
          <span className="level-pill">LEVEL {current.level}</span>
          <div className="stage-title" key={current.name}>
            <span>{current.icon}</span>
            <div><b>{current.name}</b><small>{current.note}</small></div>
          </div>
          <div className="resource-status">
            <span className={`cycle-badge ${fruitType}`}>이번 나무 · {fruitType === "apple" ? "🍎 사과" : "🍊 귤"}</span>
            <span className="stock-badge"><i>✦</i> 보유 비료 <b>{fertilizerStock}</b>개</span>
            <span className="total-badge">누적 사용 <b>{fertilizer}</b> / 20</span>
          </div>
        </div>

        <div className={`plant-stage ${isFeeding ? "feeding" : ""} ${celebrate ? "celebrate" : ""}`}>
          <div className="sun sun-one" /><div className="sun sun-two" />
          <img src={current.image} alt={`${current.name} 성장 단계 캐릭터`} key={current.image} />
          {isFeeding && (
            <>
              <div className="nutrients"><i>✦</i><i>✦</i><i>✦</i></div>
              <div className="feeding-aura" />
              <div className="feeding-sparkles" aria-hidden="true">
                {Array.from({ length: 20 }, (_, index) => (
                  <i key={index} style={{
                    "--spark-x": `${18 + ((index * 23) % 66)}%`,
                    "--spark-y": `${14 + ((index * 31) % 68)}%`,
                    "--spark-delay": `${(index % 6) * .04}s`
                  }}>✦</i>
                ))}
              </div>
            </>
          )}
        </div>

        <div className="progress-panel">
          <div className="progress-labels">
            <span>{next ? `다음 단계 · ${next.name}` : "최종 단계 달성"}</span>
            <b>{next ? `${fertilizer - current.need} / ${next.need - current.need}` : "20 / 20"}</b>
          </div>
          <div className="progress-track" aria-label="현재 단계 성장 게이지">
            <div className="progress-fill" style={{ width: `${progress}%` }}><span /></div>
          </div>
          <p>{next ? `비료 ${next.need - fertilizer}개를 더 주면 ${next.name}(으)로 성장해요!` : "축하해요! 모든 성장 단계를 완성했어요."}</p>
        </div>

        <button className="feed-button" onClick={feed} disabled={isFeeding || !next || fertilizerStock <= 0}>
          <span className="button-glow" />
          <span className="bag"><i>✦</i>🌱</span>
          <span className="feed-copy">
            <b>{!next ? "성장 완료!" : fertilizerStock <= 0 ? "비료가 부족해요" : isFeeding ? "쑥쑥 자라는 중…" : "비료 주기"}</b>
            {next && fertilizerStock > 0 && <small>클릭해서 성장 에너지 +1</small>}
          </span>
          {next && fertilizerStock > 0 && <span className="feed-cost">-1</span>}
        </button>
        <button className="reset-button" onClick={reset}>처음부터 다시 키우기 ↻</button>
      </section>

      <section className="fruit-vault" id="vault" aria-label="수확한 열매 보관함">
        <div className="vault-heading">
          <span className="vault-icon">🧺</span>
          <div>
            <span className="mini-label">MY HARVEST</span>
            <h2>나의 열매 보관함</h2>
            <p>열매 단계까지 키우면 이곳에 수확한 열매가 차곡차곡 쌓여요.</p>
          </div>
          <div className="harvest-total"><small>총 수확</small><b>{harvestedFruits}</b><span>개</span></div>
        </div>
        <div className="vault-shelf">
          {Array.from({ length: Math.max(6, Math.min(12, harvestedFruits)) }, (_, index) => (
            <div className={`fruit-slot ${index < harvestedFruits ? "filled" : ""}`} key={index}>
              {index < harvestedFruits ? <><span>{index % 2 === 0 ? "🍎" : "🍊"}</span><small>{index + 1}번째 열매</small></> : <><i>+</i><small>비어 있음</small></>}
            </div>
          ))}
          {harvestedFruits > 12 && <div className="more-fruits">+{harvestedFruits - 12}<small>더 많은 열매</small></div>}
        </div>
        <div className="vault-tip"><span>🌱</span><p><b>수확 후에는 다시 씨앗부터!</b>성장 한 바퀴마다 새로운 열매 하나를 얻을 수 있어요.</p></div>
      </section>

      <section className="journey" id="journey">
        <div className="section-heading">
          <span className="mini-label">GROWTH JOURNEY</span>
          <h2>한눈에 보는 성장 여정</h2>
          <p>작은 시작부터 빛나는 결실까지, 모든 과정이 소중해요.</p>
        </div>
        <div className="stage-list">
          {displayStages.map((stage, index) => {
            const reached = fertilizer >= stage.need;
            const active = index === currentIndex;
            return (
              <div className={`journey-stage ${reached ? "reached" : ""} ${active ? "active" : ""}`} key={stage.name}>
                <div className="journey-image"><img src={stage.image} alt="" /></div>
                <div className="journey-dot">{reached ? "✓" : index + 1}</div>
                <b>{stage.name}</b>
                <span>Lv.{stage.level}</span>
                <small>{stage.need === 0 ? "가입 즉시" : `누적 ${stage.need}개`}</small>
              </div>
            );
          })}
        </div>
      </section>

      <section className="criteria" id="criteria">
        <div><span>✦</span><p><b>성장은 차곡차곡 쌓여요</b>비료 개수는 누적되며, 각 단계에 도달하면 새로운 모습이 열려요.</p></div>
        <div className="criteria-chips">
          {displayStages.map((stage) => <span key={stage.name}><b>{stage.name}</b>{stage.need}개</span>)}
        </div>
      </section>

      <footer><span>씨앗별 성장 정원</span><p>오늘의 작은 배움이 내일의 큰 열매가 됩니다.</p></footer>

      {celebrate && (
        <div className="celebration-overlay" role="status" aria-live="polite">
          <div className="screen-flash" />
          <div className="celebration-burst" />
          <div className="confetti" aria-hidden="true">
            {Array.from({ length: 28 }, (_, index) => (
              <i key={index} style={{
                "--x": `${(index * 37) % 100}%`,
                "--delay": `${(index % 7) * .06}s`,
                "--spin": `${180 + (index % 5) * 70}deg`,
                "--color": ["#8fcf78", "#ffcf5c", "#ff91a9", "#8cd6d1", "#fff3a0"][index % 5]
              }} />
            ))}
          </div>
          <div className="celebration-card">
            <span className="achievement-label">GROWTH ACHIEVEMENT</span>
            <strong className="level-up-shout">LEVEL UP!</strong>
            <div className="stage-change">
              <span>{displayStages[Math.max(0, currentIndex - 1)].icon} {displayStages[Math.max(0, currentIndex - 1)].name}</span>
              <i>➜</i>
              <b>{current.icon} {current.name}</b>
            </div>
            <div className="celebration-image"><img src={current.image} alt="" /></div>
            <div className="level-number">LEVEL {current.level}</div>
            <h2>짠! <em>{current.name}</em>(으)로 성장했어요!</h2>
            <p>{current.note}</p>
            <div className="reward-chip">{currentIndex === 4 ? "🧺 열매 1개가 보관함에 저장됐어요!" : "✦ 새로운 성장 모습 해금"}</div>
          </div>
        </div>
      )}
    </main>
  );
}
