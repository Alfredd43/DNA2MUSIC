import type { AppProps } from 'next/app'
import { useEffect } from 'react'
import Navbar from '../components/Navbar'
import '../styles/globals.css'

export default function App({ Component, pageProps }: AppProps) {
  useEffect(() => {
    document.documentElement.classList.add('dark')
  }, [])
  return (
    <>
      <Navbar />
      <Component {...pageProps} />
    </>
  )
} 