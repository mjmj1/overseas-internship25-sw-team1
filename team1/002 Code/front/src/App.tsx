import { BrowserRouter as Router } from "react-router-dom";
import TimeTable from "./components/TimeTable";
// import Calendar from "./components/Calendar";
import Header from "./components/Header";
import Footer from "./components/Footer";
import "./App.css";
import { useRef } from "react";

const App = () => {
    const timetableRef = useRef<HTMLDivElement | null>(null);
    const calendarRef = useRef<HTMLDivElement | null>(null);

    const scrollToTimeTable = () => {
        if (timetableRef.current) {
            timetableRef.current.scrollIntoView({ behavior: "smooth" });
        }
    };

    const scrollToCalendar = () => {
        if (calendarRef.current) {
            calendarRef.current.scrollIntoView({ behavior: "smooth" });
        }
    };

    return (
        <Router> {/* ✅ BrowserRouter 추가 */}
            <div className="app-container">
                <Header scrollToTimeTable={scrollToTimeTable} scrollToCalendar={scrollToCalendar} />
                <main className="main-content">
                    <div ref={timetableRef}>
                        <TimeTable />
                    </div>
                    <div ref={calendarRef}>
                        {/*<Calendar />*/}
                    </div>
                </main>
                <Footer />
            </div>
        </Router>
    );
};

export default App;
