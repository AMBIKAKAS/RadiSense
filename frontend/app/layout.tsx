// @ts-expect-error - allow side-effect CSS import without types
import "leaflet/dist/leaflet.css";
// @ts-expect-error - allow side-effect CSS import without types
import "./globals.css";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body style={{ height: "100vh", width: "100vw" }}>
        {children}
      </body>
    </html>
  );
}
