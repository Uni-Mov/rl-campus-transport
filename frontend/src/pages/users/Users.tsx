import { useState, useEffect } from "react";

export default function Users(){
    const [users,setUsers] = useState([]);
    useEffect(() => {
        fetch("http://localhost:5000/users/")
        .then(res => {
            if (!res.ok) {
                throw new Error('Network response was not ok');
            }
            return res.json();
        })
        .then(data => {
            console.log('Users data:', data);
            setUsers(data);
        })
        .catch(error => {
            console.error('Error fetching users:', error);
        });
    }, []);
    console.log(users);
    return (
        <div>
            <h1 className="flex flex-col items-center justify-center">I am a little example of user:
            </h1>
            <div className="flex flex-col items-center justify-center">
            {users.map(user => (
                <div key={user.id}>
                    <h2>{user.name}</h2>
                    <p>{user.email}</p>
                </div>
                
            ))}
            </div>
        </div>
    );
}
