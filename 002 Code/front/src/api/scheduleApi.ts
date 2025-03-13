import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api/table/view";
export interface ScheduleItem {
    id: number;
    courseCode: string;
    resourceCode: string;
    facultyCode: string;
    session: string;
    lecturer: string;
    combineBy: string;
    dayOfWeek: string;
    roomCapacity: number;
    courseCapacity: number;
    startTime: string;
    minPerSession: number;
}

// 백엔드에서 데이터를 가져와 ScheduleItem[] 형태로 변환
export const fetchSchedule = async (facultyCodes: string[]): Promise<ScheduleItem[]> => {
    try {
        const queryString = facultyCodes.map(code => `facultyCode=${code}`).join("&");
        const response = await axios.get(`${API_BASE_URL}/?${queryString}`);
        return response.data.map((item: any): ScheduleItem => ({
            id: item.id,
            courseCode: item.CourseCode,
            resourceCode: item.ResourceCode,
            facultyCode: item.FacultyCode,
            session: item.Session,
            lecturer: item.Lecturer,
            combineBy: item.CombineBy,
            dayOfWeek: item.DayOfWeek,
            roomCapacity: item.RoomCapacity,
            courseCapacity: item.CourseCapacity,
            startTime: item.StartTime.toString().padStart(2, "0") + ":00",
            minPerSession: item.MinPerSession
        }));
    } catch (error) {
        console.error("Error fetching schedule:", error);
        throw error;
    }
};

