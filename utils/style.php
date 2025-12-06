<script src="https://cdn.tailwindcss.com"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
<style>
    :root {
        --primary-green: #10b981;
        --deep-green: #059669;
        --light-green: #d1fae5;
        --gray-50: #f9fafb;
        --gray-900: #111827;
    }

    body {
        background-color: var(--gray-50);
        color: var(--gray-900);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .sidebar {
        background: linear-gradient(135deg, var(--deep-green), var(--primary-green));
        color: white;
        transition: all 0.3s ease;
    }

    .nav-item {
        color: rgba(255, 255, 255, 0.8);
        cursor: pointer;
        padding: 12px 20px;
        border-radius: 8px;
        margin: 8px 0;
        transition: all 0.2s ease;
    }

    .nav-item:hover {
        background-color: rgba(255, 255, 255, 0.15);
        color: white;
    }

    .nav-item.active {
        background-color: rgba(255, 255, 255, 0.25);
        color: white;
        font-weight: 600;
    }

    .btn-primary {
        background-color: var(--primary-green);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .btn-primary:hover {
        background-color: var(--deep-green);
        transform: translateY(-2px);
        box-shadow: 0 10px 15px rgba(16, 185, 129, 0.3);
    }

    .btn-secondary {
        background-color: white;
        border: 2px solid var(--primary-green);
        color: var(--primary-green);
        padding: 10px 20px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .btn-secondary:hover {
        background-color: var(--light-green);
    }

    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        border-left: 4px solid var(--primary-green);
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    .stat-card h3 {
        color: var(--gray-900);
        font-size: 14px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #6b7280;
        margin-bottom: 8px;
    }
    
    .stat-card .number {
        font-size: 32px;
        font-weight: 700;
        color: var(--deep-green);
    }
    
    .table-container {
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    .table-container table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .table-container th {
        background-color: var(--light-green);
        color: var(--deep-green);
        padding: 16px;
        text-align: left;
        font-weight: 600;
        border: none;
    }
    
    .table-container td {
        padding: 16px;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .table-container tbody tr:hover {
        background-color: #f3f4f6;
    }
    
    .badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .badge-success {
        background-color: var(--light-green);
        color: var(--deep-green);
    }
    
    .badge-warning {
        background-color: #fed7aa;
        color: #92400e;
    }
    
    .badge-danger {
        background-color: #fecaca;
        color: #991b1b;
    }
    
    .form-input {
        width: 100%;
        padding: 12px;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        font-size: 14px;
        transition: all 0.2s ease;
    }
    
    .form-input:focus {
        outline: none;
        border-color: var(--primary-green);
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
    }
    
    .page {
        display: none;
    }

    .page.active {
        display: block;
    }
    
    .header {
        background: white;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        border-bottom: 2px solid var(--light-green);
    }
    
    .modal {
        display: none;
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: rgba(0, 0, 0, 0.5);
        z-index: 1000;
        align-items: center;
        justify-content: center;
    }
    
    .modal.active {
        display: flex;
    }
    
    .modal-content {
        background: white;
        border-radius: 12px;
        padding: 32px;
        width: 90%;
        max-width: 600px;
        max-height: 90vh;
        overflow-y: auto;
    }
    
    .chart-container {
        position: relative;
        height: 300px;
        margin-top: 20px;
    }
</style>