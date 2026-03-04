const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');


const app = express();

//middlewares
app.use(cors());
app.use(express.json());

//Multer storage configuration
const storage = multer.diskStorage({
    destination: function(req, file, cb) {
        cb(null, 'uploads/');
    },
    filename: function(req, file, cb) {
        const uniqueName = Date.now() + path.extname(file.originalname);
        cb(null, uniqueName);
    }
});
const upload = multer({ storage: storage });


//Upload route
app.post('/upload', upload.single('image'), async(req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ message: 'No file uploaded' });
        }

        console.log("File received:", req.file.path);

        //Send image to python

        const formData = new FormData();
        formData.append('image', fs.createReadStream(req.file.path));

        const pythonResponse = await axios.post(
            'http://localhost:8000/analyze',
            formData, {
                headers: formData.getHeaders()
            }
        );

        console.log("Response from python :", pythonResponse.data);

        //send python response to frontend
        res.status(200).json({
            message: 'Image processed successfully',
            description: pythonResponse.data.description
        });

    } catch (error) {
        console.error(error.message);
        res.status(500).json({ message: 'Error processing image' });
    }
});




//Test route
app.get('/', (req, res) => {
    res.send('Backend is running');
});


const PORT = 5000;

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});