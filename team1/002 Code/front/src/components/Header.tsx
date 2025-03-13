import { useNavigate } from "react-router-dom"; // ✅ React Router 추가
import { FaTable } from "react-icons/fa";
import "./Header.css";

interface HeaderProps {
    scrollToTimeTable: () => void;
    // scrollToCalendar: () => void;
}

const Header: React.FC<HeaderProps> = ({ scrollToTimeTable }) => {
    const navigate = useNavigate();

    const goToHome = () => {
        navigate("/");
    };

    return (
        <header className="header">
            <div className="header-left">
                <img
                    src="/assets/ucsi_uni_logo.png"
                    alt="UCSI University Logo"
                    className="header-logo"
                    onClick={goToHome}
                    style={{ cursor: "pointer" }}
                />
                <img src="/assets/qs_world_ranking_2025.png" alt="QS World Ranking 2025" className="header-ranking" />
            </div>

            <nav className="header-right">
                <button className="header-link" onClick={scrollToTimeTable}>
                    <FaTable className="timetable-icon" />
                    <div className="header-text">
                        <span className="header-line"></span> TimeTable <span className="header-line"></span>
                    </div>
                </button>

                {/*<button className="header-link" onClick={scrollToCalendar}>*/}
                {/*    <FaRegCalendarAlt className="calendar-icon" />*/}
                {/*    <div className="header-text">*/}
                {/*        <span className="header-line"></span> Calendar <span className="header-line"></span>*/}
                {/*    </div>*/}
                {/*</button>*/}
            </nav>
        </header>
    );
};

export default Header;
