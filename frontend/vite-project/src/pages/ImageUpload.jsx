import React, { useRef, useState } from 'react'

const ImageUpload = () => {
    const[selectedFile, setSelectedFile] = useState(null);
    const[preview, setPreview] = useState(null);
    const[description, setDescription] = useState("");
    const[loading, setLoading] = useState(false);
    const videoRef = useRef(null);

    const handleFileChange =(e) =>{
        if(!e.target.files || e.target.files.length === 0)return;
        const file = e.target.files[0];
        setPreview(URL.createObjectURL(file));
        setSelectedFile(file);
        setDescription("");
    }

    const handleTimeUpdate = () =>{
        if (!videoRef.current) return;

        const currentTime = videoRef.current.currentTime;

        if(currentTime >= 10 && currentTime < 10.5 ){
            videoRef.current.pause();
            alert("Suspicious activity detected")
        }
    };

    const handleUpload = async () =>{
        if(!selectedFile) return;

        const formData = new FormData();
        formData.append("image", selectedFile);

        try{
            setLoading(true);

            const response = await fetch("http://localhost:5000/upload",{
                method: "POST",
                body: formData
            });

            const data = await response.json();

            if (response.ok){
                setDescription(data.description);
            }else{
                setDescription("error"+ data.message);
            }
        }catch(error){
            console.error(error);
            setDescription("Server error. check backend.");
        }finally{
            setLoading(false);
        }
    };
  return (
    <div className='min-h-screen bg-gray-100 flex items-center justify-center p-6'>
        <div className='bg-white p-8 rounded-2xl shadow-xl w-full max-w-xl'>
            <h1 className='text-3xl font-bold mb-6 text-center text-gray-800'>AI Image Description</h1>

            <input type='file' accept='video/*' onChange={handleFileChange} className='mb-4 block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-500 file:text-white hover:file:bg-blue-600'/>
            {preview && selectedFile?.type.startsWith("video") &&(
                <video ref={videoRef} src={preview} controls autoPlay onTimeUpdate={handleTimeUpdate} className='mb-4 rounded-xl max-h-64 w-full object-cover'/>
            )}
            <button onClick={handleUpload} disabled={loading} className='w-full bg-blue-500 hover:bg-blue-600 py-3 rounded-xl font-semibold transition text-white'>
                {loading? "Processing.": "Description"}
            </button>
            {description  &&(
                <div className='mt-6 bg-gray-50 p-4 rounded-xl border'>
                    <h2 className='font-semibold mb-2 text-gray-700'>Generate Description:</h2>
                    <p className='text-gray-600'>{description}</p>
                </div>
            )}
        </div>
      
    </div>
  )
}

export default ImageUpload
