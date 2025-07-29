import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Components
const Dashboard = ({ stats, onNavigate }) => (
  <div className="p-8">
    <h1 className="text-3xl font-bold mb-8 text-gray-800">Goods Receipt & Issue Management</h1>
    
    {/* Stats Cards */}
    <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
      <div className="bg-blue-500 text-white p-6 rounded-lg shadow-lg">
        <h3 className="text-lg font-semibold">Materials</h3>
        <p className="text-3xl font-bold">{stats?.total_materials || 0}</p>
      </div>
      <div className="bg-green-500 text-white p-6 rounded-lg shadow-lg">
        <h3 className="text-lg font-semibold">Locations</h3>
        <p className="text-3xl font-bold">{stats?.total_locations || 0}</p>
      </div>
      <div className="bg-yellow-500 text-white p-6 rounded-lg shadow-lg">
        <h3 className="text-lg font-semibold">Pending Invoices</h3>
        <p className="text-3xl font-bold">{stats?.pending_invoices || 0}</p>
      </div>
      <div className="bg-purple-500 text-white p-6 rounded-lg shadow-lg">
        <h3 className="text-lg font-semibold">Goods Receipts</h3>
        <p className="text-3xl font-bold">{stats?.total_receipts || 0}</p>
      </div>
      <div className="bg-red-500 text-white p-6 rounded-lg shadow-lg">
        <h3 className="text-lg font-semibold">Goods Issues</h3>
        <p className="text-3xl font-bold">{stats?.total_issues || 0}</p>
      </div>
    </div>

    {/* Action Buttons */}
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <button 
        onClick={() => onNavigate('materials')}
        className="bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-lg font-semibold transition-colors"
      >
        Material Master
      </button>
      <button 
        onClick={() => onNavigate('goods-receipt')}
        className="bg-green-600 hover:bg-green-700 text-white p-4 rounded-lg font-semibold transition-colors"
      >
        Goods Receipt
      </button>
      <button 
        onClick={() => onNavigate('goods-issue')}
        className="bg-purple-600 hover:bg-purple-700 text-white p-4 rounded-lg font-semibold transition-colors"
      >
        Goods Issue
      </button>
      <button 
        onClick={() => onNavigate('invoices')}
        className="bg-yellow-600 hover:bg-yellow-700 text-white p-4 rounded-lg font-semibold transition-colors"
      >
        Invoice Management
      </button>
      <button 
        onClick={() => onNavigate('stock-overview')}
        className="bg-indigo-600 hover:bg-indigo-700 text-white p-4 rounded-lg font-semibold transition-colors"
      >
        Stock Overview
      </button>
      <button 
        onClick={() => onNavigate('locations')}
        className="bg-gray-600 hover:bg-gray-700 text-white p-4 rounded-lg font-semibold transition-colors"
      >
        Locations
      </button>
      <button 
        onClick={() => onNavigate('purchase-orders')}
        className="bg-orange-600 hover:bg-orange-700 text-white p-4 rounded-lg font-semibold transition-colors"
      >
        Purchase Orders
      </button>
      <button 
        onClick={() => onNavigate('movements')}
        className="bg-teal-600 hover:bg-teal-700 text-white p-4 rounded-lg font-semibold transition-colors"
      >
        Stock Movements
      </button>
    </div>
  </div>
);

const MaterialMaster = ({ onBack }) => {
  const [materials, setMaterials] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    material_code: '',
    material_description: '',
    material_group: '',
    unit_of_measure: 'PC'
  });

  useEffect(() => {
    fetchMaterials();
  }, []);

  const fetchMaterials = async () => {
    try {
      const response = await axios.get(`${API}/materials`);
      setMaterials(response.data);
    } catch (error) {
      console.error('Error fetching materials:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/materials`, formData);
      setFormData({ material_code: '', material_description: '', material_group: '', unit_of_measure: 'PC' });
      setShowForm(false);
      fetchMaterials();
    } catch (error) {
      console.error('Error creating material:', error);
      alert('Error creating material');
    }
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Material Master</h2>
        <div className="space-x-4">
          <button 
            onClick={() => setShowForm(!showForm)}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            {showForm ? 'Cancel' : 'Add Material'}
          </button>
          <button 
            onClick={onBack}
            className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg"
          >
            Back to Dashboard
          </button>
        </div>
      </div>

      {showForm && (
        <div className="bg-white p-6 rounded-lg shadow-lg mb-6">
          <h3 className="text-lg font-semibold mb-4">Add New Material</h3>
          <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Material Code"
              value={formData.material_code}
              onChange={(e) => setFormData({...formData, material_code: e.target.value})}
              className="border border-gray-300 rounded-lg px-3 py-2"
              required
            />
            <input
              type="text"
              placeholder="Material Description"
              value={formData.material_description}
              onChange={(e) => setFormData({...formData, material_description: e.target.value})}
              className="border border-gray-300 rounded-lg px-3 py-2"
              required
            />
            <input
              type="text"
              placeholder="Material Group"
              value={formData.material_group}
              onChange={(e) => setFormData({...formData, material_group: e.target.value})}
              className="border border-gray-300 rounded-lg px-3 py-2"
            />
            <select
              value={formData.unit_of_measure}
              onChange={(e) => setFormData({...formData, unit_of_measure: e.target.value})}
              className="border border-gray-300 rounded-lg px-3 py-2"
            >
              <option value="PC">PC - Pieces</option>
              <option value="KG">KG - Kilograms</option>
              <option value="LT">LT - Liters</option>
              <option value="MT">MT - Meters</option>
              <option value="EA">EA - Each</option>
            </select>
            <button type="submit" className="col-span-2 bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg">
              Create Material
            </button>
          </form>
        </div>
      )}

      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Code</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Group</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">UoM</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {materials.map((material) => (
              <tr key={material.id}>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">{material.material_code}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{material.material_description}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{material.material_group || '-'}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{material.unit_of_measure}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{new Date(material.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const GoodsReceiptForm = ({ onBack }) => {
  const [materials, setMaterials] = useState([]);
  const [locations, setLocations] = useState([]);
  const [purchaseOrders, setPurchaseOrders] = useState([]);
  const [invoices, setInvoices] = useState([]);
  const [formData, setFormData] = useState({
    po_id: '',
    po_number: '',
    invoice_id: '',
    vendor_code: '',
    vendor_name: '',
    location_id: '',
    posting_date: new Date().toISOString().split('T')[0],
    document_date: new Date().toISOString().split('T')[0],
    header_text: '',
    items: [{ material_id: '', material_code: '', quantity: 0, unit_price: 0 }]
  });

  useEffect(() => {
    fetchMaterials();
    fetchLocations();
    fetchPurchaseOrders();
    fetchInvoices();
  }, []);

  const fetchMaterials = async () => {
    try {
      const response = await axios.get(`${API}/materials`);
      setMaterials(response.data);
    } catch (error) {
      console.error('Error fetching materials:', error);
    }
  };

  const fetchLocations = async () => {
    try {
      const response = await axios.get(`${API}/locations`);
      setLocations(response.data);
    } catch (error) {
      console.error('Error fetching locations:', error);
    }
  };

  const fetchPurchaseOrders = async () => {
    try {
      const response = await axios.get(`${API}/purchase-orders`);
      setPurchaseOrders(response.data);
    } catch (error) {
      console.error('Error fetching purchase orders:', error);
    }
  };

  const fetchInvoices = async () => {
    try {
      const response = await axios.get(`${API}/invoices`);
      setInvoices(response.data);
    } catch (error) {
      console.error('Error fetching invoices:', error);
    }
  };

  const addItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, { material_id: '', material_code: '', quantity: 0, unit_price: 0 }]
    });
  };

  const updateItem = (index, field, value) => {
    const updatedItems = [...formData.items];
    updatedItems[index][field] = value;
    
    if (field === 'material_id') {
      const material = materials.find(m => m.id === value);
      if (material) {
        updatedItems[index]['material_code'] = material.material_code;
      }
    }
    
    setFormData({ ...formData, items: updatedItems });
  };

  const removeItem = (index) => {
    const updatedItems = formData.items.filter((_, i) => i !== index);
    setFormData({ ...formData, items: updatedItems });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/goods-receipts`, formData);
      alert('Goods Receipt created successfully!');
      onBack();
    } catch (error) {
      console.error('Error creating goods receipt:', error);
      alert('Error creating goods receipt');
    }
  };

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Create Goods Receipt</h2>
        <button 
          onClick={onBack}
          className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg"
        >
          Back to Dashboard
        </button>
      </div>

      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-lg">
        <div className="grid grid-cols-2 gap-4 mb-6">
          <select
            value={formData.po_id}
            onChange={(e) => {
              const po = purchaseOrders.find(p => p.id === e.target.value);
              setFormData({
                ...formData, 
                po_id: e.target.value,
                po_number: po?.po_number || '',
                vendor_code: po?.vendor_code || '',
                vendor_name: po?.vendor_name || ''
              });
            }}
            className="border border-gray-300 rounded-lg px-3 py-2"
          >
            <option value="">Select Purchase Order</option>
            {purchaseOrders.map(po => (
              <option key={po.id} value={po.id}>{po.po_number} - {po.vendor_name}</option>
            ))}
          </select>

          <select
            value={formData.invoice_id}
            onChange={(e) => setFormData({...formData, invoice_id: e.target.value})}
            className="border border-gray-300 rounded-lg px-3 py-2"
          >
            <option value="">Select Invoice</option>
            {invoices.map(invoice => (
              <option key={invoice.id} value={invoice.id}>{invoice.invoice_number} - {invoice.vendor_name}</option>
            ))}
          </select>

          <input
            type="text"
            placeholder="Vendor Code"
            value={formData.vendor_code}
            onChange={(e) => setFormData({...formData, vendor_code: e.target.value})}
            className="border border-gray-300 rounded-lg px-3 py-2"
            required
          />

          <input
            type="text"
            placeholder="Vendor Name"
            value={formData.vendor_name}
            onChange={(e) => setFormData({...formData, vendor_name: e.target.value})}
            className="border border-gray-300 rounded-lg px-3 py-2"
            required
          />

          <select
            value={formData.location_id}
            onChange={(e) => setFormData({...formData, location_id: e.target.value})}
            className="border border-gray-300 rounded-lg px-3 py-2"
            required
          >
            <option value="">Select Location</option>
            {locations.map(location => (
              <option key={location.id} value={location.id}>{location.plant_code} - {location.storage_location}</option>
            ))}
          </select>

          <input
            type="date"
            value={formData.posting_date}
            onChange={(e) => setFormData({...formData, posting_date: e.target.value})}
            className="border border-gray-300 rounded-lg px-3 py-2"
            required
          />

          <input
            type="date"
            value={formData.document_date}
            onChange={(e) => setFormData({...formData, document_date: e.target.value})}
            className="border border-gray-300 rounded-lg px-3 py-2"
            required
          />

          <input
            type="text"
            placeholder="Header Text"
            value={formData.header_text}
            onChange={(e) => setFormData({...formData, header_text: e.target.value})}
            className="border border-gray-300 rounded-lg px-3 py-2"
          />
        </div>

        <h3 className="text-lg font-semibold mb-4">Items</h3>
        {formData.items.map((item, index) => (
          <div key={index} className="grid grid-cols-5 gap-2 mb-2 items-center">
            <select
              value={item.material_id}
              onChange={(e) => updateItem(index, 'material_id', e.target.value)}
              className="border border-gray-300 rounded-lg px-3 py-2"
              required
            >
              <option value="">Select Material</option>
              {materials.map(material => (
                <option key={material.id} value={material.id}>{material.material_code} - {material.material_description}</option>
              ))}
            </select>
            <input
              type="number"
              placeholder="Quantity"
              value={item.quantity}
              onChange={(e) => updateItem(index, 'quantity', parseFloat(e.target.value) || 0)}
              className="border border-gray-300 rounded-lg px-3 py-2"
              required
            />
            <input
              type="number"
              placeholder="Unit Price"
              value={item.unit_price}
              onChange={(e) => updateItem(index, 'unit_price', parseFloat(e.target.value) || 0)}
              className="border border-gray-300 rounded-lg px-3 py-2"
              step="0.01"
            />
            <span className="text-sm text-gray-600">
              Total: {(item.quantity * item.unit_price).toFixed(2)}
            </span>
            <button
              type="button"
              onClick={() => removeItem(index)}
              className="bg-red-500 hover:bg-red-600 text-white px-3 py-2 rounded-lg"
            >
              Remove
            </button>
          </div>
        ))}

        <div className="flex justify-between items-center mt-4">
          <button
            type="button"
            onClick={addItem}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg"
          >
            Add Item
          </button>
          <button
            type="submit"
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg"
          >
            Create Goods Receipt
          </button>
        </div>
      </form>
    </div>
  );
};

const StockOverview = ({ onBack }) => {
  const [stock, setStock] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStock();
  }, []);

  const fetchStock = async () => {
    try {
      const response = await axios.get(`${API}/stock-overview`);
      setStock(response.data);
    } catch (error) {
      console.error('Error fetching stock:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Stock Overview</h2>
        <button 
          onClick={onBack}
          className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-lg"
        >
          Back to Dashboard
        </button>
      </div>

      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Material Code</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Description</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Plant</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Storage Location</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Current Stock</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">UoM</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Updated</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {stock.map((item) => (
              <tr key={item.id}>
                <td className="px-6 py-4 text-sm font-medium text-gray-900">{item.material_code}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{item.material_description}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{item.plant_code}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{item.storage_location}</td>
                <td className="px-6 py-4 text-sm text-gray-500">
                  <span className={`${item.current_quantity < 0 ? 'text-red-600' : 'text-green-600'} font-semibold`}>
                    {item.current_quantity}
                  </span>
                </td>
                <td className="px-6 py-4 text-sm text-gray-500">{item.unit_of_measure}</td>
                <td className="px-6 py-4 text-sm text-gray-500">{new Date(item.last_updated).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

function App() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [stats, setStats] = useState(null);

  useEffect(() => {
    if (currentView === 'dashboard') {
      fetchStats();
    }
  }, [currentView]);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/dashboard/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const renderView = () => {
    switch (currentView) {
      case 'materials':
        return <MaterialMaster onBack={() => setCurrentView('dashboard')} />;
      case 'goods-receipt':
        return <GoodsReceiptForm onBack={() => setCurrentView('dashboard')} />;
      case 'stock-overview':
        return <StockOverview onBack={() => setCurrentView('dashboard')} />;
      default:
        return <Dashboard stats={stats} onNavigate={setCurrentView} />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {renderView()}
    </div>
  );
}

export default App;