async function loadUsers(){
  const secret = document.getElementById('secret').value;
  const res = await fetch(`/api/users?secret=${encodeURIComponent(secret)}`);
  if(res.status !== 200){
    document.getElementById('users').innerText = 'Unauthorized or error';
    return;
  }
  const users = await res.json();
  let html = '<table><tr><th>ID</th><th>Username</th><th>Name</th><th>Banned</th><th>Actions</th></tr>';
  users.forEach(u => {
    html += `<tr>
      <td>${u.telegram_id}</td>
      <td>@${u.username || ''}</td>
      <td>${u.first_name || ''}</td>
      <td>${u.banned}</td>
      <td>
        <button onclick="ban(${u.telegram_id})">Ban</button>
        <button onclick="unban(${u.telegram_id})">Unban</button>
      </td>
    </tr>`;
  });
  html += '</table>';
  document.getElementById('users').innerHTML = html;
}

async function ban(tg){
  const secret = document.getElementById('secret').value;
  await fetch('/api/ban', {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify({secret, telegram_id: tg})});
  loadUsers();
}
async function unban(tg){
  const secret = document.getElementById('secret').value;
  await fetch('/api/unban', {method:'POST', headers:{'content-type':'application/json'}, body: JSON.stringify({secret, telegram_id: tg})});
  loadUsers();
}
async function loadStats(){
  const secret = document.getElementById('secret').value;
  const res = await fetch(`/api/stats?secret=${encodeURIComponent(secret)}`);
  if(res.status !== 200){ document.getElementById('stats').innerText = 'Unauthorized'; return; }
  const s = await res.json();
  document.getElementById('stats').innerText = `Total: ${s.total} | Banned: ${s.banned} | Premium: ${s.premium}`;
}
