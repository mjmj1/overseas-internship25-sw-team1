import React from "react";
import "./Footer.css"; // ✅ 스타일 import

const Footer: React.FC = () => {
    return (
        <footer className="footer">
            <p>© 2025 UCSI University. All rights reserved.</p>
        </footer>
    );
};

export default Footer; // ✅ Footer 컴포넌트 내보내기
