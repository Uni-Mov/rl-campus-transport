import { Routes, Route } from "react-router-dom"
import Home from "../pages/home/Home"
import Clients from "../pages/clients/Clients"
import Login from "../pages/login/Login"
import Header from "../components/organisms/Header/Header"
import Footer from "../components/organisms/Footer"
import Register from "../pages/register/Register"
import { Error404 } from "../pages/404/error"
import Contact from "../pages/contact/Contact"
import Travel from "../pages/travel/travel"

export default function App() {
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/clients" element={<Clients />} />
          <Route path="/login" element={<Login />}/>
          <Route path="/register" element={<Register />}/>
          <Route path="/contact" element={<Contact />}/>
          <Route path="/travel" element={<Travel />}/>
          <Route path="*" element={<Error404 />} />
        </Routes>
      </main>
      <Footer />
    </>
  )
}
