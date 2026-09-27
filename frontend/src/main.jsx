import { motion } from 'framer-motion'
import { ArrowRight, BarChart3, BookOpen, CalendarDays, CircleUserRound, FileText, Library, Plus, Search, UsersRound } from 'lucide-react'
import { createRoot } from 'react-dom/client'
import { useEffect, useState } from 'react'
import './style.css'

const features = [
  ['Book Search', Search],
  ['Issue & Return', BookOpen],
  ['Reservations', CalendarDays],
  ['Fine Management', BarChart3],
  ['Digital Resources', Library],
  ['Reports & Analytics', BarChart3],
  ['User Management', UsersRound],
]

const API = 'http://127.0.0.1:5000'

function LibraryDesk({ onExit }) {
  const [section, setSection] = useState('overview')
  const [data, setData] = useState({ members: [], books: [], issues: [], reservations: [], stats: {} })
  const [message, setMessage] = useState('')
  const [form, setForm] = useState({ title: '', author: '', category: '', isbn: '', copies: 1, cover: '', description: '' })

  const loadOverview = () => fetch(`${API}/api/admin/overview`, { credentials: 'include' })
    .then((response) => response.ok ? response.json() : Promise.reject(new Error('Please sign in as library staff first.')))
    .then(setData)
    .catch((error) => setMessage(error.message))

  useEffect(loadOverview, [])

  const addBook = (event) => {
    event.preventDefault()
    fetch(`${API}/api/admin/books`, { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(form) })
      .then((response) => response.json().then((payload) => ({ ok: response.ok, payload })))
      .then(({ ok, payload }) => { setMessage(payload.message || payload.error); if (ok) { setForm({ title: '', author: '', category: '', isbn: '', copies: 1, cover: '', description: '' }); loadOverview() } })
      .catch(() => setMessage('Could not reach the library server.'))
  }

  const nav = [['overview', 'Overview', Library], ['books', 'Add books', Plus], ['members', 'Members', UsersRound], ['circulation', 'Circulation', BookOpen], ['reservations', 'Reservations', CalendarDays], ['reports', 'Reports', FileText]]
  return <main className="desk-shell">
    <aside className="desk-sidebar"><a className="brand" href="#top" onClick={onExit}><img className="brand-logo" src="/ilms-logo.svg" alt="ILMS logo" /><strong>ILMS</strong></a><p className="desk-kicker">Library desk</p><nav>{nav.map(([key, label, Icon]) => <button className={section === key ? 'selected' : ''} onClick={() => setSection(key)} key={key}><Icon size={17} />{label}</button>)}</nav><button className="desk-exit" onClick={onExit}>← Return to home</button></aside>
    <section className="desk-main"><header className="desk-header"><div><p className="eyebrow">Staff workspace</p><h1>{nav.find(([key]) => key === section)?.[1]}</h1><p>Quiet tools for keeping the collection in motion.</p></div><a className="outline-button" href={`${API}/login`}>Staff login</a></header>{message && <div className="desk-message">{message}</div>}
      {section === 'overview' && <div className="desk-grid"><div className="desk-stat"><small>Members</small><strong>{data.stats.members || 0}</strong></div><div className="desk-stat"><small>Books</small><strong>{data.stats.books || 0}</strong></div><div className="desk-stat"><small>Active issues</small><strong>{data.stats.issued || 0}</strong></div><div className="desk-stat"><small>Calculated fines</small><strong>INR {data.stats.fines || 0}</strong></div><div className="desk-panel desk-wide"><p className="eyebrow">Recent activity</p><h2>Circulation ledger</h2>{data.issues.slice(0, 6).map((issue) => <div className="desk-row" key={issue.id}><span>{issue.full_name}</span><span>{issue.title}</span><b>{issue.status}</b></div>)}{!data.issues.length && <p className="empty-state">No circulation activity yet.</p>}</div></div>}
      {section === 'books' && <div className="desk-panel"><p className="eyebrow">Collection operations</p><h2>Add a book to the shelves.</h2><form className="desk-form" onSubmit={addBook}>{[['title', 'Title'], ['author', 'Author'], ['category', 'Category'], ['isbn', 'ISBN'], ['copies', 'Copies'], ['cover', 'Cover URL']].map(([key, label]) => <label key={key}><span>{label}</span><input name={key} value={form[key]} type={key === 'copies' ? 'number' : key === 'cover' ? 'url' : 'text'} min={key === 'copies' ? 1 : undefined} onChange={(event) => setForm({ ...form, [key]: event.target.value })} required={['title', 'author', 'category', 'isbn', 'copies'].includes(key)} /></label>)}<label className="desk-form-wide"><span>Description</span><textarea name="description" value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} rows="4" /></label><button className="gold-button" type="submit"><Plus size={17} /> Add to collection</button></form></div>}
      {section === 'members' && <><MemberActions members={data.members} books={data.books} onComplete={loadOverview} /><div className="desk-panel"><p className="eyebrow">Member directory</p><h2>All readers</h2><div className="desk-table"><div className="desk-table-head"><span>Name</span><span>Student ID</span><span>Email</span><span>Joined</span></div>{data.members.map((member) => <div className="desk-table-row" key={member.id}><span>{member.full_name}</span><span>{member.student_id}</span><span>{member.email}</span><span>{member.created_at}</span></div>)}{!data.members.length && <p className="empty-state">Sign in as staff to load member records.</p>}</div></div></>}
      {section === 'circulation' && <RecordList title="Issued books" records={data.issues} columns={['full_name', 'title', 'due_date', 'status']} />}
      {section === 'reservations' && <RecordList title="Reservation queue" records={data.reservations} columns={['full_name', 'title', 'created_at', 'status']} />}
      {section === 'reports' && <div className="desk-panel"><p className="eyebrow">Exports</p><h2>Library reports</h2><div className="desk-actions"><a className="gold-button" href={`${API}/reports/export/books`}>Books CSV</a><a className="outline-button" href={`${API}/reports/export/members`}>Members CSV</a><a className="outline-button" href={`${API}/reports/export/circulation`}>Circulation CSV</a></div></div>}
    </section>
  </main>
}

function RecordList({ title, records, columns }) { return <div className="desk-panel"><p className="eyebrow">Live records</p><h2>{title}</h2><div className="desk-table"><div className="desk-table-head">{columns.map((column) => <span key={column}>{column.replace('_', ' ')}</span>)}</div>{records.map((record, index) => <div className="desk-table-row" key={record.id || index}>{columns.map((column) => <span key={column}>{record[column] || '—'}</span>)}</div>)}{!records.length && <p className="empty-state">No records available.</p>}</div></div> }

function MemberActions({ members, books, onComplete }) {
  const [memberId, setMemberId] = useState(members[0]?.id || '')
  const [bookId, setBookId] = useState(books[0]?.id || '')
  const [message, setMessage] = useState('')
  const submit = (action) => fetch(`${API}/api/admin/${action}`, { method: 'POST', credentials: 'include', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ member_id: memberId, book_id: bookId }) })
    .then((response) => response.json().then((payload) => ({ ok: response.ok, payload })))
    .then(({ ok, payload }) => { setMessage(payload.message || payload.error); if (ok) onComplete() })
    .catch(() => setMessage('Could not reach the library server.'))
  return <div className="desk-panel action-panel"><p className="eyebrow">Circulation actions</p><h2>Move a book for a member.</h2><div className="member-actions"><label><span>Member</span><select value={memberId} onChange={(event) => setMemberId(event.target.value)}>{members.map((member) => <option value={member.id} key={member.id}>{member.full_name} · {member.student_id}</option>)}</select></label><label><span>Book</span><select value={bookId} onChange={(event) => setBookId(event.target.value)}>{books.map((book) => <option value={book.id} key={book.id}>{book.title} · {book.copies} copies</option>)}</select></label><div className="member-action-buttons"><button className="gold-button" type="button" onClick={() => submit('issue')} disabled={!memberId || !bookId}><BookOpen size={16} /> Issue book</button><button className="outline-button" type="button" onClick={() => submit('reserve')} disabled={!memberId || !bookId}><CalendarDays size={16} /> Reserve book</button></div></div>{message && <p className="action-result">{message}</p>}</div>
}

function App() {
  const [books, setBooks] = useState([])
  const [page, setPage] = useState('home')
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    const query = searchTerm ? `&q=${encodeURIComponent(searchTerm)}` : ''
    fetch(`${API}/api/books?limit=4${query}`, { credentials: 'include' })
      .then((response) => response.ok ? response.json() : [])
      .then((payload) => setBooks(payload.books || []))
      .catch(() => setBooks([]))
  }, [searchTerm])

  if (page === 'desk') return <LibraryDesk onExit={() => setPage('home')} />

  return (
    <main className="app-shell">
      <div className="library-backdrop" />
      <div className="cinematic-vignette" />
      <nav className="nav-shell">
        <a className="brand" href="#top"><img className="brand-logo" src="/ilms-logo.svg" alt="ILMS logo" /><strong>ILMS</strong></a>
        <div className="nav-links"><a className="active" href="#top">Home</a><a href="#about">About</a><a href="#books">Books</a><a href="#services">Services</a><a href="#contact">Contact</a></div>
        <label className="top-search"><Search size={15} /><input value={searchTerm} onChange={(event) => setSearchTerm(event.target.value)} placeholder="Search books..." aria-label="Search books" /></label>
        <button className="login-button" onClick={() => setPage('desk')}><CircleUserRound size={17} /> Library Desk</button>
      </nav>

      <section className="hero" id="top">
        <motion.div className="hero-copy" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }}>
          <div className="hero-logo"><BookOpen size={76} strokeWidth={1.4} /><span className="knowledge-ray">✦</span></div>
          <p className="logo-wordmark">ILMS</p>
          <h1>INTEGRATED LIBRARY<br />MANAGEMENT SYSTEM</h1>
          <p className="tagline">READ <span>|</span> LEARN <span>|</span> EXPLORE <span>|</span> GROW</p>
          <p className="hero-description">A smarter way to discover, manage and experience knowledge.</p>
          <div className="hero-actions"><a className="gold-button" href="#books">Explore Library <ArrowRight size={17} /></a><a className="outline-button" href="http://127.0.0.1:5000/login">Login to Library</a></div>
        </motion.div>
        <div className="book-stage" aria-hidden="true"><div className="floating-feature-icons"><span><BookOpen /></span><span><UsersRound /></span><span><BarChart3 /></span><span><Search /></span></div><div className="open-book"><div className="page page-left" /><div className="page page-right" /><div className="book-light" /><div className="book-cover" /></div></div>
      </section>

      <section className="feature-strip" id="services">{features.map(([label, Icon]) => <a href="#books" className="feature" key={label}><span><Icon size={21} /></span><small>{label}</small></a>)}</section>
      <section className="collection-preview" id="books"><div><img className="search-page-logo" src="/ilms-logo.svg" alt="ILMS knowledge crest" /><p className="eyebrow">Open catalog</p><h2>Knowledge, connected.</h2><p className="collection-note">Browse titles and details without signing in. Log in when you want to issue or reserve a book.</p></div><div className="book-samples">{books.length ? books.map((book) => <article key={book.id}><strong>{book.title}</strong><small>{book.author} · {book.category}</small><div className="book-actions"><a href={`${API}/book/${book.id}`}>View details</a><a href={`${API}/login?next=/book/${book.id}`}>Issue</a><a href={`${API}/login?next=/book/${book.id}`}>Reserve</a></div></article>) : <div className="book-gate"><BookOpen size={28} /><strong>Catalog unavailable</strong><span>Books could not be loaded. Please refresh and try again.</span></div>}</div></section>
      <footer id="contact">© 2026 ILMS · Connecting readers with knowledge.<span><a href="mailto:syedraqi309@gmail.com">syedraqi309@gmail.com</a> · <a href="tel:7022129961">7022129961</a> · <a href="sms:7022129961">Message</a></span></footer>
    </main>
  )
}

export default App

createRoot(document.getElementById('app')).render(<App />)
