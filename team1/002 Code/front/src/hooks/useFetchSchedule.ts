import { useState, useEffect } from "react";
import { fetchSchedule, ScheduleItem } from "../api/scheduleApi";

const useFetchSchedule = () => {
    const [schedule, setSchedule] = useState<ScheduleItem[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const getSchedule = async () => {
            try {
                const facultyCodes = [
                    "CFL", "FAS", "FBM", "FETBE", "FHTM", "FOMHS", "FOSSLA",
                    "FPS", "IASDA", "ICAD", "ICSDI", "SABE"
                ];
                const responses = await Promise.all(facultyCodes.map(code => fetchSchedule([code]))); // ✅ 각각 요청
                const mergedData = responses.flat();
                setSchedule(mergedData);
            } catch (err) {
                setError("Failed to fetch schedule data.");
            } finally {
                setLoading(false);
            }
        };

        getSchedule();
    }, []);

    return { schedule, loading, error };
};

export default useFetchSchedule;
