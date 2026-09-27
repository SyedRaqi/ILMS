from uuid import uuid4

from app import app, get_db


def test_home_page_loads():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    assert b'ILMS' in response.data
    assert b'Login to access your library account' in response.data
    assert b'Library control' not in response.data
    assert b'2026 ILMS' in response.data
    assert b'mailto:syedraqi309@gmail.com' in response.data
    assert b'tel:7022129961' in response.data
    assert b'sms:7022129961' in response.data


def test_books_are_public_but_circulation_requires_login():
    client = app.test_client()
    catalog_response = client.get('/books')
    assert catalog_response.status_code == 200
    assert b'Explore the Collection' in catalog_response.data

    api_response = client.get('/api/books?limit=1')
    assert api_response.status_code == 200
    books = api_response.get_json()['books']
    assert books

    detail_response = client.get(f"/book/{books[0]['id']}")
    assert detail_response.status_code == 200
    assert books[0]['title'].encode() in detail_response.data

    issue_response = client.post(f"/issue/{books[0]['id']}")
    assert issue_response.status_code == 302
    assert '/login' in issue_response.location


def test_admin_can_remove_active_issues_and_reservations():
    client = app.test_client()
    suffix = uuid4().hex
    with get_db() as conn:
        user_cursor = conn.execute(
            '''INSERT INTO users (full_name, student_id, email, password_hash, role)
               VALUES (?, ?, ?, ?, 'member')''',
            (f'Options Test {suffix}', f'OPT{suffix}', f'{suffix}@example.com', 'unused'),
        )
        user_id = user_cursor.lastrowid
        book_cursor = conn.execute(
            '''INSERT INTO books (title, author, category, isbn, status, copies)
               VALUES (?, ?, ?, ?, 'Issued', 0)''',
            (f'Options Test Book {suffix}', 'Test Author', 'Testing', f'OPT-{suffix}'),
        )
        book_id = book_cursor.lastrowid
        issue_cursor = conn.execute(
            "INSERT INTO borrow_records (user_id, book_id, status) VALUES (?, ?, 'Issued')",
            (user_id, book_id),
        )
        issue_id = issue_cursor.lastrowid
        reservation_cursor = conn.execute(
            "INSERT INTO reservations (user_id, book_id, status) VALUES (?, ?, 'Pending')",
            (user_id, book_id),
        )
        reservation_id = reservation_cursor.lastrowid
        conn.commit()

    try:
        anonymous_response = client.get('/admin/options')
        assert anonymous_response.status_code == 302

        client.post('/login', data={'email': 'admin@ilms.edu', 'password': 'admin123'})
        options_response = client.get('/admin/options')
        assert options_response.status_code == 200
        assert b'Circulation options' in options_response.data

        admin_response = client.get('/admin')
        assert admin_response.status_code == 200
        assert f'Options Test {suffix}'.encode() in admin_response.data
        assert f'Options Test Book {suffix}'.encode() in admin_response.data
        assert b'href="#member-directory"' in admin_response.data
        assert b'href="#circulation-ledger"' in admin_response.data
        assert b'Mark returned' in admin_response.data

        issue_response = client.post(
            f'/admin/issues/{issue_id}/remove',
            data={'return_to': 'admin'},
            follow_redirects=True,
        )
        assert issue_response.status_code == 200
        assert b'reservation notification(s) sent' in issue_response.data

        member_client = app.test_client()
        with member_client.session_transaction() as member_session:
            member_session['user_id'] = user_id
        member_dashboard = member_client.get('/dashboard')
        assert member_dashboard.status_code == 200
        assert f'The book you reserved, Options Test Book {suffix}, is available now.'.encode() in member_dashboard.data

        reservation_response = client.post(
            f'/admin/reservations/{reservation_id}/remove', follow_redirects=True
        )
        assert reservation_response.status_code == 200

        with get_db() as conn:
            issue = conn.execute(
                'SELECT returned_at, status FROM borrow_records WHERE id = ?', (issue_id,)
            ).fetchone()
            reservation = conn.execute(
                'SELECT status, notified_at FROM reservations WHERE id = ?', (reservation_id,)
            ).fetchone()
            book = conn.execute('SELECT copies, status FROM books WHERE id = ?', (book_id,)).fetchone()
        assert issue['returned_at'] is not None
        assert issue['status'] == 'Returned'
        assert reservation['status'] == 'Cancelled'
        assert reservation['notified_at'] is not None
        assert book['copies'] == 1
        assert book['status'] == 'Available'
    finally:
        with get_db() as conn:
            conn.execute('DELETE FROM borrow_records WHERE id = ?', (issue_id,))
            conn.execute('DELETE FROM reservations WHERE id = ?', (reservation_id,))
            conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
            conn.execute('DELETE FROM books WHERE id = ?', (book_id,))
            conn.commit()


def test_admin_and_reports_are_restricted_to_admins():
    suffix = uuid4().hex
    with get_db() as conn:
        member_cursor = conn.execute(
            '''INSERT INTO users (full_name, student_id, email, password_hash, role)
               VALUES (?, ?, ?, ?, 'member')''',
            (f'Role Test Member {suffix}', f'MEM{suffix}', f'member-{suffix}@example.com', 'unused'),
        )
        librarian_cursor = conn.execute(
            '''INSERT INTO users (full_name, student_id, email, password_hash, role)
               VALUES (?, ?, ?, ?, 'librarian')''',
            (f'Role Test Librarian {suffix}', f'LIB{suffix}', f'librarian-{suffix}@example.com', 'unused'),
        )
        member_id = member_cursor.lastrowid
        librarian_id = librarian_cursor.lastrowid
        conn.commit()

    try:
        for user_id in (member_id, librarian_id):
            client = app.test_client()
            with client.session_transaction() as user_session:
                user_session['user_id'] = user_id
            dashboard = client.get('/dashboard') if user_id == member_id else client.get('/librarian')
            assert dashboard.status_code == 200
            assert b'href="/admin"' not in dashboard.data
            assert b'href="/reports"' not in dashboard.data
            assert client.get('/admin').status_code == 302
            assert client.get('/reports').status_code == 302
            assert client.get('/reports/export/books').status_code == 302

        admin_client = app.test_client()
        admin_client.post('/login', data={'email': 'admin@ilms.edu', 'password': 'admin123'})
        assert admin_client.get('/admin').status_code == 200
        assert admin_client.get('/reports').status_code == 200
        assert admin_client.get('/reports/export/books').status_code == 200
    finally:
        with get_db() as conn:
            conn.execute('DELETE FROM users WHERE id IN (?, ?)', (member_id, librarian_id))
            conn.commit()


def test_register_and_login_flow():
    client = app.test_client()
    register_response = client.post(
        '/register',
        data={
            'full_name': 'Test User',
            'student_id': 'CS999',
            'email': 'testuser@example.com',
            'phone': '+91 99999 99999',
            'password': 'secret123',
            'confirm_password': 'secret123',
        },
        follow_redirects=True,
    )
    assert register_response.status_code == 200

    login_response = client.post(
        '/login',
        data={'email': 'testuser@example.com', 'password': 'secret123'},
        follow_redirects=True,
    )
    assert login_response.status_code == 200
    assert b'Welcome back' in login_response.data or b'Dashboard' in login_response.data


def test_book_issue_and_return_workflow():
    client = app.test_client()
    client.post(
        '/register',
        data={
            'full_name': 'Issue Tester',
            'student_id': 'CS111',
            'email': 'issue@example.com',
            'phone': '+91 11111 11111',
            'password': 'secret123',
            'confirm_password': 'secret123',
        },
        follow_redirects=True,
    )
    client.post('/login', data={'email': 'issue@example.com', 'password': 'secret123'}, follow_redirects=True)

    issue_response = client.post('/issue/1', follow_redirects=True)
    assert issue_response.status_code == 200
    assert b'issued' in issue_response.data.lower() or b'borrow' in issue_response.data.lower()

    return_response = client.post('/return/1', follow_redirects=True)
    assert return_response.status_code == 200
