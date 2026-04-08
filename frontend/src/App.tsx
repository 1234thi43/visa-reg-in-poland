import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Layout } from './components/Layout';
import { SlotsPage } from './pages/SlotsPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<SlotsPage title="Все города" />} />
          <Route path="pinsk" element={<SlotsPage city="Пинск" title="Пинск" />} />
          <Route path="baranovichi" element={<SlotsPage city="Барановичи" title="Барановичи" />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
