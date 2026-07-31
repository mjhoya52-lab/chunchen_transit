import "./globals.css";

export const metadata = {
  title: "씨앗별 성장 정원",
  description: "배움에 비료를 주고, 나만의 성장을 키워요."
};

export default function RootLayout({ children }) {
  return (
    <html lang="ko">
      <body>{children}</body>
    </html>
  );
}
