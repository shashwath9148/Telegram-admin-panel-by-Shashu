const secret = prompt("Enter admin secret:");
fetch(`/api/users?secret=${secret}`)
    .then(res => res.json())
    .then(users => {
        const tbody = document.querySelector("#userTable tbody");
        tbody.innerHTML = "";
        users.forEach(u => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${u.telegram_id}</td>
                <td>${u.username || ""}</td>
                <td>${u.first_name || ""}</td>
                <td>${u.banned ? "Yes" : "No"}</td>
                <td>${u.is_premium ? "Yes" : "No"}</td>
                <td>
                    ${u.banned 
                        ? `<button class="unban" onclick="unbanUser(${u.telegram_id})">Unban</button>` 
                        : `<button class="ban" onclick="banUser(${u.telegram_id})">Ban</button>`}
                </td>
            `;
            tbody.appendChild(tr);
        });
    });

function banUser(id) {
    fetch(`/api/ban`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: id, secret })
    }).then(() => location.reload());
}

function unbanUser(id) {
    fetch(`/api/unban`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ telegram_id: id, secret })
    }).then(() => location.reload());
}  const secret = document.getElementById('secret').value;
  const res = await fetch(`/api/stats?secret=${encodeURIComponent(secret)}`);
  if(res.status !== 200){ document.getElementById('stats').innerText = 'Unauthorized'; return; }
  const s = await res.json();
  document.getElementById('stats').innerText = `Total: ${s.total} | Banned: ${s.banned} | Premium: ${s.premium}`;
}
