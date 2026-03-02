const express = require('express');
const cors = require('cors');
const multer = require('multer');
const path = require('path');

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
app.post('/upload', upload.single('image'), (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ message: 'No file uploaded' });
        }

        console.log("File received:", req.file);

        res.status(200).json({
            message: 'Image uploaded successfully',
            filePath: req.file.path
        });
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: 'Server error' });
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