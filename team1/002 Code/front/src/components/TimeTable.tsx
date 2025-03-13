import { useState, useMemo } from "react";
import useFetchSchedule from "../hooks/useFetchSchedule";
import { ScheduleItem } from "../api/scheduleApi";
import "../components/TimeTable.css";

const TimeTable = () => {
    const { schedule, loading, error } = useFetchSchedule();

    // 첫 번째 카테고리 (Faculty)
    const faculties = [
        "CFL", "FAS", "FBM", "FETBE", "FHTM", "FOMHS", "FOSSLA",
        "FPS", "IASDA", "ICAD", "ICSDI", "SABE"
    ];
    const [selectedFaculty, setSelectedFaculty] = useState<string | null>(null);
    const [selectedPrefixes, setSelectedPrefixes] = useState<string[]>([]); // ✅ 다중 선택 가능하도록 변경
    const [facultyDropdownOpen, setFacultyDropdownOpen] = useState(false);
    const [prefixDropdownOpen, setPrefixDropdownOpen] = useState(false);

    const handleFacultyChange = (faculty: string) => {
        setSelectedFaculty(faculty);
        setSelectedPrefixes([]); // ✅ Faculty 변경 시 Prefix 초기화
        setFacultyDropdownOpen(false);
        setPrefixDropdownOpen(true);
    };

    // 두 번째 카테고리 (선택한 Faculty의 courseCode에서 앞 알파벳만 추출해서 그룹화)
    const coursePrefixes = useMemo(() => {
        if (!selectedFaculty) return [];
        return [...new Set(schedule
            .filter(({ facultyCode }) => facultyCode === selectedFaculty)
            .map(({ courseCode }) => courseCode.match(/^[A-Za-z]+/)?.[0] || "")
            .filter(prefix => prefix)
        )];
    }, [selectedFaculty, schedule]);

    const prefixColors = useMemo(() => {
        const colorMap: Record<string, string> = {};
        coursePrefixes.forEach((prefix, index) => {
            const hue = (0 + (index * 15)) % 20; // 0~20도 범위에서 색상 변화 (빨강 계열 유지)
            const lightness = 20 + (index * 7) % 60; // 밝기 변화 (20~80%)
            colorMap[prefix] = `hsl(${hue}, 80%, ${lightness}%)`; // 빨강 계열 (채도 높여서 선명하게)
        });
        return colorMap;
    }, [coursePrefixes]);



    // 다중 선택
    const handlePrefixChange = (prefix: string) => {
        setSelectedPrefixes(prev =>
            prev.includes(prefix) ? prev.filter(p => p !== prefix) : [...prev, prefix]
        );
    };

    // 선택된 Prefix 중 하나라도 포함된 강의 필터링
    const filteredCourses = useMemo(() => {
        if (selectedPrefixes.length === 0) return [];
        return schedule.filter(({ courseCode }) =>
            selectedPrefixes.some(prefix => courseCode.startsWith(prefix))
        );
    }, [selectedPrefixes, schedule]);

    // 타임테이블 매핑
    const daysOfWeek = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
    const timeSlots = Array.from({ length: 14 }, (_, i) => `${9 + i}:00`.padStart(5, "0"));

    const timetableMap: Record<string, Record<string, ScheduleItem[]>> = {};
    daysOfWeek.forEach(day => {
        timetableMap[day] = {};
        timeSlots.forEach(time => {
            timetableMap[day][time] = [];
        });
    });

    // 타임테이블에 강의 추가 (MinPerSession 적용)
    filteredCourses.forEach(item => {
        const day = item.dayOfWeek;
        const startTime = item.startTime;
        const duration = item.minPerSession;

        const startIndex = timeSlots.indexOf(startTime);
        if (startIndex !== -1) {
            for (let i = 0; i < duration; i++) {
                const time = timeSlots[startIndex + i];
                if (time && timetableMap[day] && timetableMap[day][time]) {
                    timetableMap[day][time].push(item);
                }
            }
        }
    });

    return (
        <div className="timetable-container">
            <h2>Timetable</h2>

            <div className="category-container">
                <label className="category-label">Faculty :</label>
                <div className="category-group">
                    <button className="category-title" onClick={() => setFacultyDropdownOpen((prev) => !prev)}>
                        {selectedFaculty || "Select Faculty"} ▼
                    </button>
                    {facultyDropdownOpen && (
                        <div className="subcategory-list">
                            {faculties.map((faculty) => (
                                <div
                                    key={faculty}
                                    className={`category-option ${selectedFaculty === faculty ? "selected" : ""}`}
                                    onClick={() => handleFacultyChange(faculty)}
                                >
                                    {faculty}
                                </div>
                            ))}
                        </div>
                    )}
                </div>
                {selectedFaculty && (
                    <>
                        <label className="category-label">Course :</label>
                        <div className="category-group">
                            <button className="category-title" onClick={() => setPrefixDropdownOpen((prev) => !prev)}>
                                {selectedPrefixes.length > 0 ? selectedPrefixes.join(", ") : "Select Course"} ▼
                            </button>
                            {prefixDropdownOpen && (
                                <div className="subcategory-list">
                                    {coursePrefixes.map((prefix) => (
                                        <label key={prefix} className="category-option">
                                            <input
                                                type="checkbox"
                                                value={prefix}
                                                checked={selectedPrefixes.includes(prefix)}
                                                onChange={() => handlePrefixChange(prefix)}
                                            />
                                            {prefix}
                                        </label>
                                    ))}
                                </div>
                            )}
                        </div>
                    </>
                )}

            </div>

            {/* 로딩 & 에러 처리 */}
            {loading ? <p>Loading timetable...</p> : error ? <p>{error}</p> : null}

            {/* 타임테이블 */}
            <table className="timetable">
                <thead>
                <tr>
                    <th></th>
                    {daysOfWeek.map(day => (
                        <th key={day}>{day}</th>
                    ))}
                </tr>
                </thead>
                <tbody>
                {timeSlots.map((time) => (
                    <tr key={time}>
                        <td className="time-slot">{time}</td>
                        {daysOfWeek.map(day => (
                            <td key={`${day}-${time}`} className="class-cell">
                                {timetableMap[day][time].length > 0 && (
                                    <div className="class-info-multiple">
                                        {timetableMap[day][time].map((cls, index) => (
                                            <div
                                                key={index}
                                                className="class-info"
                                                style={{ backgroundColor: prefixColors[cls.courseCode.substring(0, 3)] || "hsl(0, 60%, 40%)" }} // 기본 색상 추가
                                            >
                                                <strong>{cls.courseCode}</strong>
                                                <p>{cls.lecturer}</p>
                                                <p>{cls.resourceCode}</p>
                                            </div>

                                        ))}
                                    </div>
                                )}
                            </td>
                        ))}
                    </tr>
                ))}
                </tbody>
            </table>
        </div>
    );
};

export default TimeTable;
