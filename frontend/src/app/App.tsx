import { Routes, Route } from "react-router-dom"
import Home from "../pages/home/Home"
import Clients from "../pages/clients/Clients"
import Header from "../components/organisms/Header"
import Footer from "../components/organisms/Footer"
import { Error404 } from "../pages/404/error"

export default function App() {
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/clients" element={<Clients />} />
          <Route path="*" element={<Error404 />} />
        </Routes>
      </main>
      <Footer />
    </>
  )
}
