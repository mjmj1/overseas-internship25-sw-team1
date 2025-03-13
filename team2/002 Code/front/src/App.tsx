import React from "react";
import Header from "./components/Header"; // ✅ 헤더 추가
import Timetable from "./components/Timetable"; // ✅ 타임테이블 추가
import Footer from "./components/Footer.tsx"; // ✅ 푸터 추가
import "./App.css"; // ✅ 스타일 import

const App: React.FC = () => {
    return (
        <div className="app">
            <Header />
            <Timetable />
            <Footer /> {/* ✅ 푸터 추가 */}
        </div>
    );
};

export default App;