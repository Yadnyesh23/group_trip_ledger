import { Navigate, Route, Routes } from 'react-router-dom';
import ProtectedRoute from './routes/ProtectedRoute';
import AppLayout from './layouts/AppLayout';
import Landing from './pages/Landing';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import TripLayout, { Overview } from './pages/TripLayout';
import Members from './pages/Members';
import Expenses from './pages/Expenses';
import Balances from './pages/Balances';
import Report from './pages/Report';
import Profile from './pages/Profile';
import About from './pages/About';

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/trips" element={<Dashboard />} />
          <Route path="/trips/:tripId" element={<TripLayout />}>
            <Route index element={<Overview />} />
            <Route path="members" element={<Members />} />
            <Route path="expenses" element={<Expenses />} />
            <Route path="balances" element={<Balances />} />
            <Route path="report" element={<Report />} />
          </Route>
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Profile />} />
          <Route path="/about" element={<About />} />
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
