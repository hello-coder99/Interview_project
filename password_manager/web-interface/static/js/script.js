async function fetch_password(){
    let Name=document.getElementById("Name").value;
    try{
        const response=await fetch("http://localhost:5000/get_pass",{
            method:"POST",
            headers:{
                "Content-Type":"application/json"
            },
		body:JSON.stringify({"name":Name})
        });
        if(!response.ok){
            throw new Error(`Http error status : ${response.status}`);
        }
        const result=await response.json();
	document.getElementById("output1").innerText=result["status"];
    }
    catch(error){
        console.log("Error occured :",error);
    }
}

async function get_all(){
	try{
		const response=await fetch("http://localhost:5000/listed",{
			method:"POST"
		});
		if(!response.ok){
			throw new Error(`HTTP error status : ${response.status}`);
		}
		const result=await response.json();
		document.getElementById("output2").innerText=result["status"];
		alert(result["status"]);
	}
	catch(error){
		console.log("Error occurred :",error);
	}
}

async function store_data(){
	let Name2=document.getElementById("Name2").value;
	let pass=document.getElementById("pass").value;

	try{
		const response=await fetch("http://localhost:5000/store_pass",{
			method:"POST",
			headers:{
				"Content-Type":"application/json"
			},
			body: JSON.stringify({"name":Name2,"password":pass})
		});
		if(!response.ok){
			throw new Error(`HTTP error status : ${response.status}`);
		}
		const result=await response.json();
		document.getElementById("output3").innerText=result["status"];
	}
	catch(error){
		console.log("Error occurred :",error);
	}
}

async function delete_data(){
	let Name3=document.getElementById("Name3").value;
	try{
		const response=await fetch("http://localhost:5000/delete_pass",{
			method: "POST",
			headers:{
				"Content-Type":"application/json"
			},
			body: JSON.stringify({"name":Name3})
		});
		if(!response.ok){
			throw new Error(`HTTP error status : ${response.status}`);
		}
		const result=await response.json();
		document.getElementById("output4").innerText=result["status"];
	}
	catch(error){
		console.log("Error occurred :",error);
	}
}

async function copyText(){
	const text=document.getElementById("output1").innerText;
	try{
		await navigator.clipboard.writeText(text);
		alert("copied");
	}
	catch(err){
		alert("failed to copy");
	}
}
