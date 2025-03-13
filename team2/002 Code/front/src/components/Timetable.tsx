import React, { useState } from "react";
import "./Timetable.css";

// 📌 단과대 리스트
const faculties = ["All", "CFL", "FAS", "FBM", "FETBE", "FHTM", "FOMHS", "FOSSLA", "FPS", "IASDA", "ICAD", "ICSDI", "SABE"];

// 📌 요일 리스트
const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];

// 📌 시간 슬롯 리스트 (30분 단위)
const timeSlots = [
    "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
    "12:00", "12:30", "13:00", "13:30", "14:00", "14:30", "15:00", "15:30",
    "16:00", "16:30", "17:00", "17:30", "18:00", "18:30", "19:00", "19:30",
    "20:00", "20:30", "21:00", "21:30"
];

const exampleSchedule: {
    assignedDay: string;
    assignedTimeSlot: string;
    group: string;
    lecturer: string;
    assignedRoom: string;
}[] = [
    // 📌 Monday
    { assignedDay: "Monday", assignedTimeSlot: "08:00-11:00", group: "MATH101_S1", lecturer: "Dr. Kim", assignedRoom: "A01-12" },
    { assignedDay: "Monday", assignedTimeSlot: "08:30-12:00", group: "PHY201_S2", lecturer: "Dr. Lee", assignedRoom: "B02-14" },
    { assignedDay: "Monday", assignedTimeSlot: "09:00-11:30", group: "CHEM101_S3", lecturer: "Dr. Park", assignedRoom: "C03-15" },
    { assignedDay: "Monday", assignedTimeSlot: "13:00-16:00", group: "CS102_S4", lecturer: "Dr. Choi", assignedRoom: "D04-08" },
    { assignedDay: "Monday", assignedTimeSlot: "16:00-19:00", group: "BIO102_S6", lecturer: "Dr. Yoon", assignedRoom: "F06-09" },

    // 📌 Tuesday
    { assignedDay: "Tuesday", assignedTimeSlot: "08:00-10:30", group: "ECON101_S1", lecturer: "Dr. Kim", assignedRoom: "H08-11" },
    { assignedDay: "Tuesday", assignedTimeSlot: "09:00-12:00", group: "MUSIC301_S2", lecturer: "Dr. Lee", assignedRoom: "I09-12" },
    { assignedDay: "Tuesday", assignedTimeSlot: "13:30-16:30", group: "PHIL202_S4", lecturer: "Dr. Choi", assignedRoom: "K11-16" },
    { assignedDay: "Tuesday", assignedTimeSlot: "15:00-18:00", group: "SOC102_S5", lecturer: "Dr. Han", assignedRoom: "L12-13" },

    // 📌 Wednesday
    { assignedDay: "Wednesday", assignedTimeSlot: "08:00-10:00", group: "ART202_S1", lecturer: "Dr. Yoon", assignedRoom: "N14-15" },
    { assignedDay: "Wednesday", assignedTimeSlot: "09:30-12:30", group: "ENG301_S2", lecturer: "Dr. Kim", assignedRoom: "O15-17" },
    { assignedDay: "Wednesday", assignedTimeSlot: "11:00-14:00", group: "STAT101_S3", lecturer: "Dr. Lee", assignedRoom: "P16-19" },
    { assignedDay: "Wednesday", assignedTimeSlot: "13:00-16:00", group: "MATH305_S4", lecturer: "Dr. Park", assignedRoom: "Q17-21" },

    // 📌 Thursday
    { assignedDay: "Thursday", assignedTimeSlot: "08:30-11:30", group: "MATH204_S1", lecturer: "Dr. Shin", assignedRoom: "T20-18" },
    { assignedDay: "Thursday", assignedTimeSlot: "10:00-13:00", group: "CS202_S2", lecturer: "Dr. Lee", assignedRoom: "U21-16" },
    { assignedDay: "Thursday", assignedTimeSlot: "11:30-14:30", group: "STAT201_S3", lecturer: "Dr. Park", assignedRoom: "V22-14" },
    { assignedDay: "Thursday", assignedTimeSlot: "15:30-18:30", group: "ECON301_S5", lecturer: "Dr. Jang", assignedRoom: "X24-12" },
    { assignedDay: "Thursday", assignedTimeSlot: "18:00-21:00", group: "CHEM203_S6", lecturer: "Dr. Song", assignedRoom: "Y25-11" },

    // 📌 Friday
    { assignedDay: "Friday", assignedTimeSlot: "08:00-10:30", group: "BIO301_S1", lecturer: "Dr. Kim", assignedRoom: "Z26-10" },
    { assignedDay: "Friday", assignedTimeSlot: "09:00-12:00", group: "ENG302_S2", lecturer: "Dr. Lee", assignedRoom: "AA27-19" },
    { assignedDay: "Friday", assignedTimeSlot: "10:30-13:30", group: "MATH402_S3", lecturer: "Dr. Park", assignedRoom: "BB28-17" },
    { assignedDay: "Friday", assignedTimeSlot: "15:00-18:00", group: "COMP503_S5", lecturer: "Dr. Jang", assignedRoom: "DD30-13" },
    { assignedDay: "Friday", assignedTimeSlot: "17:30-20:30", group: "CHEM303_S6", lecturer: "Dr. Song", assignedRoom: "EE31-12" },
];



// 📌 "08:00-10:00" → { start: "08:00", end: "10:00" } 변환
const parseTimeRange = (timeRange: string): { start: string; end: string } => {
    const [start, end] = timeRange.split("-").map(t => t.trim());
    return { start, end };
};

// 📌 과목별 색상 매핑 (연한 파스텔톤 적용)
const courseColorMap: Record<string, string> = {};
const colors = [
    "rgba(255, 205, 178, 0.85)", "rgba(255, 237, 186, 0.85)", "rgba(186, 255, 201, 0.85)", "rgba(186, 225, 255, 0.85)",
    "rgba(220, 186, 255, 0.85)", "rgba(255, 186, 217, 0.85)", "rgba(255, 223, 186, 0.85)", "rgba(211, 255, 186, 0.85)"
];

let colorIndex = 0;
const getColorForCourse = (courseCode: string) => {
    if (!courseColorMap[courseCode]) {
        courseColorMap[courseCode] = colors[colorIndex % colors.length];
        colorIndex++;
    }
    return courseColorMap[courseCode];
};

const Timetable: React.FC = () => {
    const [selectedFaculty, setSelectedFaculty] = useState<string>("All");

    return (
        <div className="timetable-wrapper">
            <div className="faculty-select-container">
                <label htmlFor="faculty-select" className="faculty-label">Faculty Code:</label>
                <select
                    id="faculty-select"
                    value={selectedFaculty}
                    onChange={(e) => setSelectedFaculty(e.target.value)}
                    className="faculty-select"
                >
                    {faculties.map((faculty, index) => (
                        <option key={index} value={faculty}>{faculty}</option>
                    ))}
                </select>
            </div>

            <div className="timetable-container">
                <table className="timetable">
                    <thead>
                    <tr>
                        <th>Day\Time</th>
                        {timeSlots.map((slot, index) => (
                            <th key={index}>{slot}</th>
                        ))}
                    </tr>
                    </thead>
                    <tbody>
                    {days.map((day, dayIndex) => {
                        const occupancy = Array.from({ length: 6 }, () => Array(timeSlots.length).fill(false));
                        const cells = Array.from({ length: 6 }, () => Array(timeSlots.length).fill(null));
                        const events = exampleSchedule
                            .filter(event => event.assignedDay === day)
                            .map(event => ({
                                ...parseTimeRange(event.assignedTimeSlot),
                                group: event.group,
                                lecturer: event.lecturer,
                                room: event.assignedRoom
                            }));

                        events.forEach((event) => {
                            const startIdx = timeSlots.indexOf(event.start);
                            const endIdx = timeSlots.indexOf(event.end);
                            const spanCount = endIdx - startIdx;

                            let rowIdx = -1;
                            for (let r = 0; r < 6; r++) {
                                let available = true;
                                for (let i = startIdx; i < endIdx; i++) {
                                    if (occupancy[r][i]) {
                                        available = false;
                                        break;
                                    }
                                }
                                if (available) {
                                    rowIdx = r;
                                    break;
                                }
                            }
                            if (rowIdx === -1) rowIdx = 0;

                            for (let i = startIdx; i < endIdx; i++) {
                                occupancy[rowIdx][i] = true;
                            }
                            cells[rowIdx][startIdx] = { ...event, span: spanCount };
                        });

                        return (
                            <React.Fragment key={dayIndex}>
                                <tr>
                                    <td className="day" rowSpan={6}>{day}</td>
                                    {cells[0].map((cell, idx) => (
                                        cell ? (
                                            <td key={`${dayIndex}-0-${idx}`} className="cell highlighted"
                                                colSpan={cell.span} style={{ backgroundColor: getColorForCourse(cell.group) }}>
                                                <div className="course-info">
                                                    <div className="course-code">{cell.group} <span className="room">({cell.room})</span></div>
                                                    <div className="course-prof">{cell.lecturer}</div>
                                                </div>
                                            </td>
                                        ) : <td key={`${dayIndex}-0-${idx}`} className="cell"></td>
                                    ))}
                                </tr>
                                {[1, 2, 3, 4, 5].map(rowNum => (
                                    <tr key={`${dayIndex}-row-${rowNum}`} className={rowNum === 5 ? "last" : ""}>
                                        {cells[rowNum].map((cell, idx) => (
                                            cell ? (
                                                <td key={`${dayIndex}-${rowNum}-${idx}`} className="cell highlighted"
                                                    colSpan={cell.span} style={{ backgroundColor: getColorForCourse(cell.group) }}>
                                                    <div className="course-info">
                                                        <div className="course-code">{cell.group} <span className="room">({cell.room})</span></div>
                                                        <div className="course-prof">{cell.lecturer}</div>
                                                    </div>
                                                </td>
                                            ) : <td key={`${dayIndex}-${rowNum}-${idx}`} className="cell"></td>
                                        ))}
                                    </tr>
                                ))}
                            </React.Fragment>
                        );
                    })}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default Timetable;
