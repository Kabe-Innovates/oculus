import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import TransactionDetail from './pages/TransactionDetail';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/transaction/:id" element={<TransactionDetail />} />
      </Routes>
    </Router>
  );
}

export default App;
