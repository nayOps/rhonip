import { Html, Head, Main, NextScript } from 'next/document'

export default function Document() {
  return (
    <Html lang="fr">
      <Head>
        {/* Anti-FOUC si JS est bloqué: forcer l'affichage du body */}
        <style dangerouslySetInnerHTML={{ __html: 'body{display:block!important}' }} />
      </Head>
      <body>
        <Main />
        <NextScript />
        <script
          // Fallback anti-FOUC: ensure body is visible even if hydration stalls
          dangerouslySetInnerHTML={{ __html: "document.body && (document.body.style.display='block')" }}
        />
      </body>
    </Html>
  )
}
