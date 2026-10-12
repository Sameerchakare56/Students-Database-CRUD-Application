/* ==========================================================================
   STUDENT DATABASE MANAGEMENT SYSTEM - FRONTEND APPLICATION LOGIC
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // --- State Management ---
    let currentState = {
        page: 1,
        limit: 10,
        total: 0,
        search: '',
        courseFilter: '',
        students: [],
        activeStudentId: null
    };

    // --- DOM Elements ---
    const navStudentsBtn = document.getElementById('nav-students');
    const navAiBtn = document.getElementById('nav-ai');
    const studentsTab = document.getElementById('students-tab');
    const aiTab = document.getElementById('ai-tab');
    const pageTitle = document.getElementById('page-title');
    const pageSubtitle = document.getElementById('page-subtitle');

    // Metrics
    const statTotalStudents = document.getElementById('stat-total-students');
    const statCoursesCount = document.getElementById('stat-courses-count');
    const statAvgGpa = document.getElementById('stat-avg-gpa');
    const statLatestCode = document.getElementById('stat-latest-code');

    // Controls
    const searchInput = document.getElementById('search-input');
    const btnClearSearch = document.getElementById('btn-clear-search');
    const courseFilterSelect = document.getElementById('course-filter-select');
    const btnRefreshList = document.getElementById('btn-refresh-list');
    const btnSeedData = document.getElementById('btn-seed-data');

    // Table & Pagination
    const studentsTableBody = document.getElementById('students-table-body');
    const tableSummaryText = document.getElementById('table-summary-text');
    const btnPrevPage = document.getElementById('btn-prev-page');
    const btnNextPage = document.getElementById('btn-next-page');
    const pageIndicator = document.getElementById('page-indicator');

    // Student Add/Edit Modal
    const studentModal = document.getElementById('student-modal');
    const modalTitle = document.getElementById('modal-title');
    const studentForm = document.getElementById('student-form');
    const btnOpenAddModal = document.getElementById('btn-open-add-modal');
    const btnCloseModal = document.getElementById('btn-close-modal');
    const btnCancelModal = document.getElementById('btn-cancel-modal');

    // View Modal
    const viewModal = document.getElementById('view-modal');
    const viewProfileBody = document.getElementById('view-profile-body');
    const btnCloseViewModal = document.getElementById('btn-close-view-modal');
    const btnCloseView = document.getElementById('btn-close-view');

    // Delete Modal
    const deleteModal = document.getElementById('delete-modal');
    const deleteStudentName = document.getElementById('delete-student-name');
    const deleteStudentCode = document.getElementById('delete-student-code');
    const btnCloseDeleteModal = document.getElementById('btn-close-delete-modal');
    const btnCancelDelete = document.getElementById('btn-cancel-delete');
    const btnConfirmDelete = document.getElementById('btn-confirm-delete');

    // AI Form & Chat
    const aiQueryForm = document.getElementById('ai-query-form');
    const aiQuestionInput = document.getElementById('ai-question-input');
    const aiChatBox = document.getElementById('ai-chat-box');
    const ollamaStatusText = document.getElementById('ollama-status-text');

    // --- Toast Notification Utility ---
    function showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const iconClass = type === 'success' ? 'fa-circle-check' : (type === 'error' ? 'fa-circle-xmark' : 'fa-circle-info');
        toast.innerHTML = `<i class="fa-solid ${iconClass}"></i> <span>${message}</span>`;
        
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }, 3500);
    }

    // --- Tab Navigation ---
    navStudentsBtn.addEventListener('click', () => {
        navStudentsBtn.classList.add('active');
        navAiBtn.classList.remove('active');
        studentsTab.style.display = 'block';
        aiTab.style.display = 'none';
        pageTitle.textContent = 'Student Directory';
        pageSubtitle.textContent = 'Manage student profiles with Create, Read, Update, and Delete operations.';
    });

    navAiBtn.addEventListener('click', () => {
        navAiBtn.classList.add('active');
        navStudentsBtn.classList.remove('active');
        studentsTab.style.display = 'none';
        aiTab.style.display = 'block';
        pageTitle.textContent = 'Ollama Local AI Assistant';
        pageSubtitle.textContent = 'Ask natural language questions grounded in your SQLite database records.';
    });

    // --- API Data Fetching ---
    async function loadStudents() {
        studentsTableBody.innerHTML = `
            <tr>
                <td colspan="7" class="loading-cell">
                    <div class="spinner"></div> Loading student records...
                </td>
            </tr>
        `;

        const skip = (currentState.page - 1) * currentState.limit;
        const params = new URLSearchParams({
            skip: skip.toString(),
            limit: currentState.limit.toString()
        });

        if (currentState.search) params.append('search', currentState.search);
        if (currentState.courseFilter) params.append('course', currentState.courseFilter);

        try {
            const response = await fetch(`/api/students?${params.toString()}`);
            if (!response.ok) throw new Error('Failed to load students');

            const data = await response.json();
            currentState.students = data.students;
            currentState.total = data.total;

            renderStudentsTable(data.students);
            updatePaginationControls();
            updateMetrics();
            populateCourseFilterOptions();
        } catch (error) {
            console.error('Error fetching students:', error);
            studentsTableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="loading-cell" style="color: var(--accent-rose)">
                        <i class="fa-solid fa-triangle-exclamation"></i> Error loading records. Is FastAPI server running?
                    </td>
                </tr>
            `;
            showToast('Error loading student records from backend.', 'error');
        }
    }

    // --- Render Table Rows ---
    function renderStudentsTable(students) {
        if (!students || students.length === 0) {
            studentsTableBody.innerHTML = `
                <tr>
                    <td colspan="7" class="loading-cell">
                        <i class="fa-solid fa-folder-open" style="font-size: 1.8rem; margin-bottom: 8px; display: block;"></i>
                        No student records found. Click "Add New Student" or "Seed Dummy Data".
                    </td>
                </tr>
            `;
            return;
        }

        studentsTableBody.innerHTML = students.map(student => {
            const gpaVal = student.gpa !== null ? student.gpa.toFixed(2) : 'N/A';
            let gpaClass = 'medium';
            if (student.gpa >= 3.6) gpaClass = 'high';
            else if (student.gpa < 3.0 && student.gpa !== null) gpaClass = 'low';

            return `
                <tr>
                    <td><span class="code-badge">${escapeHtml(student.student_code)}</span></td>
                    <td>
                        <strong style="color: var(--text-primary);">${escapeHtml(student.name)}</strong>
                    </td>
                    <td>
                        <div><i class="fa-solid fa-envelope" style="color: var(--text-muted); font-size: 0.8rem; margin-right: 4px;"></i> ${escapeHtml(student.email)}</div>
                        <div style="font-size: 0.8rem; color: var(--text-secondary);"><i class="fa-solid fa-phone" style="font-size: 0.75rem; margin-right: 4px;"></i> ${escapeHtml(student.phone)}</div>
                    </td>
                    <td>${escapeHtml(student.dob)}</td>
                    <td>
                        ${student.course ? `<span class="course-badge">${escapeHtml(student.course)}</span>` : '<span style="color: var(--text-muted);">Unassigned</span>'}
                    </td>
                    <td>
                        <span class="gpa-badge ${gpaClass}">${gpaVal}</span>
                    </td>
                    <td class="text-right">
                        <div class="action-buttons">
                            <button class="btn-action view" data-id="${student.id}" title="View Details">
                                <i class="fa-solid fa-eye"></i>
                            </button>
                            <button class="btn-action edit" data-id="${student.id}" title="Edit Student">
                                <i class="fa-solid fa-pen-to-square"></i>
                            </button>
                            <button class="btn-action delete" data-id="${student.id}" data-name="${escapeHtml(student.name)}" data-code="${escapeHtml(student.student_code)}" title="Delete Student">
                                <i class="fa-solid fa-trash-can"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    }

    // --- Populate Course Options ---
    function populateCourseFilterOptions() {
        const courses = new Set();
        currentState.students.forEach(s => {
            if (s.course) courses.add(s.course);
        });

        const currentSelected = courseFilterSelect.value;
        const options = ['<option value="">All Courses</option>'];
        courses.forEach(c => {
            options.push(`<option value="${escapeHtml(c)}" ${c === currentSelected ? 'selected' : ''}>${escapeHtml(c)}</option>`);
        });

        courseFilterSelect.innerHTML = options.join('');
    }

    // --- Update Metrics Header Cards ---
    function updateMetrics() {
        statTotalStudents.textContent = currentState.total;
        
        // Courses count
        const courses = new Set(currentState.students.map(s => s.course).filter(Boolean));
        statCoursesCount.textContent = courses.size;

        // Avg GPA
        const gpas = currentState.students.map(s => s.gpa).filter(g => g !== null && g !== undefined);
        if (gpas.length > 0) {
            const avg = gpas.reduce((a, b) => a + b, 0) / gpas.length;
            statAvgGpa.textContent = avg.toFixed(2);
        } else {
            statAvgGpa.textContent = "0.00";
        }

        // Latest Code
        if (currentState.students.length > 0) {
            statLatestCode.textContent = currentState.students[0].student_code;
        }
    }

    // --- Pagination Controls ---
    function updatePaginationControls() {
        const start = (currentState.page - 1) * currentState.limit + 1;
        const end = Math.min(currentState.page * currentState.limit, currentState.total);
        const totalPages = Math.ceil(currentState.total / currentState.limit) || 1;

        if (currentState.total === 0) {
            tableSummaryText.textContent = "Showing 0 of 0 students";
        } else {
            tableSummaryText.textContent = `Showing ${start}-${end} of ${currentState.total} students`;
        }

        pageIndicator.textContent = `Page ${currentState.page} of ${totalPages}`;
        btnPrevPage.disabled = currentState.page <= 1;
        btnNextPage.disabled = currentState.page >= totalPages;
    }

    btnPrevPage.addEventListener('click', () => {
        if (currentState.page > 1) {
            currentState.page--;
            loadStudents();
        }
    });

    btnNextPage.addEventListener('click', () => {
        const totalPages = Math.ceil(currentState.total / currentState.limit);
        if (currentState.page < totalPages) {
            currentState.page++;
            loadStudents();
        }
    });

    // --- Search & Filter Handlers ---
    let searchTimeout;
    searchInput.addEventListener('input', (e) => {
        const val = e.target.value.trim();
        btnClearSearch.style.display = val ? 'block' : 'none';
        
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentState.search = val;
            currentState.page = 1;
            loadStudents();
        }, 300);
    });

    btnClearSearch.addEventListener('click', () => {
        searchInput.value = '';
        btnClearSearch.style.display = 'none';
        currentState.search = '';
        currentState.page = 1;
        loadStudents();
    });

    courseFilterSelect.addEventListener('change', (e) => {
        currentState.courseFilter = e.target.value;
        currentState.page = 1;
        loadStudents();
    });

    btnRefreshList.addEventListener('click', () => {
        loadStudents();
        showToast('Refreshed student list.', 'info');
    });

    // --- Seed Demo Data Button ---
    btnSeedData.addEventListener('click', async () => {
        try {
            const response = await fetch('/api/students/seed/demo', { method: 'POST' });
            const result = await response.json();
            showToast(result.message, 'success');
            loadStudents();
        } catch (error) {
            showToast('Error seeding demo data.', 'error');
        }
    });

    // --- Modal Management ---
    function openModal(modal) {
        modal.classList.add('active');
    }

    function closeModal(modal) {
        modal.classList.remove('active');
    }

    // Add Student
    btnOpenAddModal.addEventListener('click', () => {
        modalTitle.innerHTML = '<i class="fa-solid fa-user-plus"></i> Add New Student';
        studentForm.reset();
        document.getElementById('form-student-id').value = '';
        openModal(studentModal);
    });

    btnCloseModal.addEventListener('click', () => closeModal(studentModal));
    btnCancelModal.addEventListener('click', () => closeModal(studentModal));

    // Form Submit (Create or Update)
    studentForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const studentId = document.getElementById('form-student-id').value;
        const isUpdate = !!studentId;

        const payload = {
            student_code: document.getElementById('form-student-code').value.trim() || null,
            name: document.getElementById('form-name').value.trim(),
            email: document.getElementById('form-email').value.trim(),
            phone: document.getElementById('form-phone').value.trim(),
            dob: document.getElementById('form-dob').value,
            course: document.getElementById('form-course').value.trim() || null,
            enrollment_date: document.getElementById('form-enrollment-date').value || null,
            gpa: document.getElementById('form-gpa').value ? parseFloat(document.getElementById('form-gpa').value) : null,
            address: document.getElementById('form-address').value.trim() || null
        };

        const url = isUpdate ? `/api/students/${studentId}` : '/api/students';
        const method = isUpdate ? 'PUT' : 'POST';

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to save student record');
            }

            const savedStudent = await response.json();
            showToast(`Student ${savedStudent.name} (${savedStudent.student_code}) ${isUpdate ? 'updated' : 'created'} successfully!`, 'success');
            closeModal(studentModal);
            loadStudents();
        } catch (error) {
            showToast(error.message, 'error');
        }
    });

    // Delegate Table Action Clicks (View, Edit, Delete)
    studentsTableBody.addEventListener('click', async (e) => {
        const btn = e.target.closest('.btn-action');
        if (!btn) return;

        const studentId = btn.dataset.id;

        if (btn.classList.contains('view')) {
            openViewModal(studentId);
        } else if (btn.classList.contains('edit')) {
            openEditModal(studentId);
        } else if (btn.classList.contains('delete')) {
            currentState.activeStudentId = studentId;
            deleteStudentName.textContent = btn.dataset.name;
            deleteStudentCode.textContent = btn.dataset.code;
            openModal(deleteModal);
        }
    });

    // Edit Modal Populate
    async function openEditModal(studentId) {
        try {
            const response = await fetch(`/api/students/${studentId}`);
            if (!response.ok) throw new Error('Could not fetch student details');

            const student = await response.json();
            modalTitle.innerHTML = '<i class="fa-solid fa-user-pen"></i> Edit Student Details';

            document.getElementById('form-student-id').value = student.id;
            document.getElementById('form-student-code').value = student.student_code;
            document.getElementById('form-name').value = student.name;
            document.getElementById('form-email').value = student.email;
            document.getElementById('form-phone').value = student.phone;
            document.getElementById('form-dob').value = student.dob;
            document.getElementById('form-course').value = student.course || '';
            document.getElementById('form-enrollment-date').value = student.enrollment_date || '';
            document.getElementById('form-gpa').value = student.gpa !== null ? student.gpa : '';
            document.getElementById('form-address').value = student.address || '';

            openModal(studentModal);
        } catch (error) {
            showToast(error.message, 'error');
        }
    }

    // View Modal Populate
    async function openViewModal(studentId) {
        try {
            const response = await fetch(`/api/students/${studentId}`);
            if (!response.ok) throw new Error('Could not fetch student profile');

            const s = await response.json();
            viewProfileBody.innerHTML = `
                <div class="profile-row">
                    <span class="profile-label">Student Code:</span>
                    <span class="code-badge">${escapeHtml(s.student_code)}</span>
                </div>
                <div class="profile-row">
                    <span class="profile-label">Full Name:</span>
                    <span class="profile-val">${escapeHtml(s.name)}</span>
                </div>
                <div class="profile-row">
                    <span class="profile-label">Email:</span>
                    <span class="profile-val">${escapeHtml(s.email)}</span>
                </div>
                <div class="profile-row">
                    <span class="profile-label">Phone:</span>
                    <span class="profile-val">${escapeHtml(s.phone)}</span>
                </div>
                <div class="profile-row">
                    <span class="profile-label">Date of Birth:</span>
                    <span class="profile-val">${escapeHtml(s.dob)}</span>
                </div>
                <div class="profile-row">
                    <span class="profile-label">Course:</span>
                    <span class="profile-val">${s.course ? escapeHtml(s.course) : 'Unassigned'}</span>
                </div>
                <div class="profile-row">
                    <span class="profile-label">Enrollment Date:</span>
                    <span class="profile-val">${s.enrollment_date ? escapeHtml(s.enrollment_date) : 'N/A'}</span>
                </div>
                <div class="profile-row">
                    <span class="profile-label">GPA:</span>
                    <span class="profile-val">${s.gpa !== null ? s.gpa.toFixed(2) : 'N/A'}</span>
                </div>
                <div class="profile-row">
                    <span class="profile-label">Address:</span>
                    <span class="profile-val">${s.address ? escapeHtml(s.address) : 'N/A'}</span>
                </div>
            `;
            openModal(viewModal);
        } catch (error) {
            showToast(error.message, 'error');
        }
    }

    btnCloseViewModal.addEventListener('click', () => closeModal(viewModal));
    btnCloseView.addEventListener('click', () => closeModal(viewModal));

    // Delete Handlers
    btnCloseDeleteModal.addEventListener('click', () => closeModal(deleteModal));
    btnCancelDelete.addEventListener('click', () => closeModal(deleteModal));

    btnConfirmDelete.addEventListener('click', async () => {
        if (!currentState.activeStudentId) return;

        try {
            const response = await fetch(`/api/students/${currentState.activeStudentId}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('Failed to delete student');

            const deleted = await response.json();
            showToast(`Student ${deleted.name} (${deleted.student_code}) deleted permanently.`, 'info');
            closeModal(deleteModal);
            loadStudents();
        } catch (error) {
            showToast(error.message, 'error');
        }
    });

    // --- AI Query Handler ---
    aiQueryForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const question = aiQuestionInput.value.trim();
        if (!question) return;

        sendAiQuestion(question);
    });

    // Suggestion Chips Click
    document.querySelectorAll('.suggestion-chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const q = chip.dataset.question;
            aiQuestionInput.value = q;
            sendAiQuestion(q);
        });
    });

    async function sendAiQuestion(question) {
        // Append user message
        appendChatMessage('user', question);
        aiQuestionInput.value = '';

        // Append loading indicator message
        const loadingId = 'loading-' + Date.now();
        appendChatMessage('system', '<div class="spinner"></div> Generating answer from database records...', loadingId);

        try {
            const response = await fetch('/api/ai/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: question, model: 'llama3.2:1b' })
            });

            const data = await response.json();

            // Update Ollama status badge
            if (data.ollama_status === 'online') {
                ollamaStatusText.textContent = `Ollama Online (${data.model_used})`;
                document.getElementById('ollama-status-badge').style.background = 'rgba(16, 185, 129, 0.15)';
                document.getElementById('ollama-status-badge').style.color = 'var(--accent-emerald)';
            } else {
                ollamaStatusText.textContent = 'Ollama Service Offline (Active Fallback Grounding)';
                document.getElementById('ollama-status-badge').style.background = 'rgba(245, 158, 11, 0.15)';
                document.getElementById('ollama-status-badge').style.color = 'var(--accent-amber)';
            }

            // Replace loading message with answer
            const loadingMsg = document.getElementById(loadingId);
            if (loadingMsg) {
                loadingMsg.querySelector('.message-content').innerHTML = escapeHtml(data.answer);
            }
        } catch (error) {
            const loadingMsg = document.getElementById(loadingId);
            if (loadingMsg) {
                loadingMsg.querySelector('.message-content').innerHTML = `<span style="color: var(--accent-rose)">Failed to query AI service. Please check backend connection.</span>`;
            }
        }

        aiChatBox.scrollTop = aiChatBox.scrollHeight;
    }

    function appendChatMessage(sender, text, msgId = null) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `ai-message ${sender}`;
        if (msgId) msgDiv.id = msgId;

        const iconClass = sender === 'user' ? 'fa-user' : 'fa-robot';
        msgDiv.innerHTML = `
            <div class="message-avatar"><i class="fa-solid ${iconClass}"></i></div>
            <div class="message-content"><p>${text}</p></div>
        `;

        aiChatBox.appendChild(msgDiv);
        aiChatBox.scrollTop = aiChatBox.scrollHeight;
    }

    // --- Helper Utility ---
    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Initial Load
    loadStudents();
});
