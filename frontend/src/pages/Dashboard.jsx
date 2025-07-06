import { useContext, useEffect, useState } from 'react';
import { AuthContext } from '../context/AuthContext';

export default function Dashboard() {
  const { authAxios } = useContext(AuthContext);
  const [events, setEvents] = useState([]);
  const [form, setForm] = useState({ title: '', description: '', date: '' });
  const [editId, setEditId] = useState(null);

  const loadEvents = async () => {
    const res = await authAxios.get('/events');
    setEvents(res.data);
  };

  useEffect(() => {
    loadEvents();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (editId) {
      await authAxios.put(`/events/${editId}`, form);
      setEditId(null);
    } else {
      await authAxios.post('/events', form);
    }
    setForm({ title: '', description: '', date: '' });
    loadEvents();
  };

  const handleEdit = (event) => {
    setEditId(event._id);
    setForm({ title: event.title, description: event.description, date: event.date.substring(0, 10) });
  };

  const handleDelete = async (id) => {
    if (window.confirm('Delete this event?')) {
      await authAxios.delete(`/events/${id}`);
      loadEvents();
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6 mt-6">
      <h2 className="text-3xl font-bold mb-4">Your Events</h2>

      <form onSubmit={handleSubmit} className="mb-6 space-y-4 border p-4 rounded shadow">
        <input
          type="text"
          required
          placeholder="Title"
          value={form.title}
          onChange={(e) => setForm({ ...form, title: e.target.value })}
          className="w-full p-2 border rounded"
        />

        <textarea
          placeholder="Description"
          value={form.description}
          onChange={(e) => setForm({ ...form, description: e.target.value })}
          className="w-full p-2 border rounded"
        />

        <input
          type="date"
          required
          value={form.date}
          onChange={(e) => setForm({ ...form, date: e.target.value })}
          className="w-full p-2 border rounded"
        />

        <button className="bg-blue-600 text-white px-4 py-2 rounded">
          {editId ? 'Update Event' : 'Add Event'}
        </button>
      </form>

      <ul>
        {events.map((ev) => (
          <li
            key={ev._id}
            className="border p-4 mb-3 rounded shadow flex justify-between items-center"
          >
            <div>
              <h3 className="font-semibold">{ev.title}</h3>
              <p>{ev.description}</p>
              <p className="text-gray-500 text-sm">{new Date(ev.date).toLocaleDateString()}</p>
            </div>
            <div className="space-x-2">
              <button
                onClick={() => handleEdit(ev)}
                className="bg-yellow-400 px-3 py-1 rounded"
              >
                Edit
              </button>
              <button
                onClick={() => handleDelete(ev._id)}
                className="bg-red-600 px-3 py-1 rounded text-white"
              >
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
