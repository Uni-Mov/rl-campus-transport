import { Routes, Route, Outlet } from "react-router-dom"
import Home from "../pages/home/Home"
import Login from "../pages/login/Login"
import Header from "../components/organisms/Header/Header"
import Footer from "../components/organisms/Footer"
import Register from "../pages/register/Register"
import { Error404 } from "../pages/404/error"
import Contact from "../pages/contact/Contact"
import Travel from "../pages/travel/travel"

function DefaultLayout() {
  return (
    <>
      <Header />
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
      <Footer />
    </>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/travel" element={<Travel />} />
      <Route element={<DefaultLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />}/>
        <Route path="/register" element={<Register />}/>
        <Route path="/contact" element={<Contact />}/>
        <Route path="*" element={<Error404 />} />
      </Route>
    </Routes>
  )
}
