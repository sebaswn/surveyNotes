

<script>
    import {MaterialApp } from 'svelte-materialify';
    import TabsBar from "./TabsBar.svelte";
    import Windows from "./Windows.svelte";
    import {openDB} from "idb";
    import {selectedMeteoStation} from "./Stores/store";


    let loadingProgress = 0;
    let setupProgress = 0;
    let finishedSetUp = false;

    dataBaseInit();


    const checkOnlineStatus = async () => {
        try {
            const online = await fetch("/testOnline");
            return online.status >= 200 && online.status < 300; // either true or false
        } catch (err) {
            return false; // definitely offline
        }
    };



    async function createDB()
    {
        setupProgress += 2;
        loadingProgress += 2;
        // Using https://github.com/jakearchibald/idb
        await openDB('notes', 1, {
            upgrade(db, oldVersion, newVersion, transaction) {
                // Switch over the oldVersion, *without breaks*, to allow the database to be incrementally upgraded.
                switch(oldVersion) {
                    case 0:
                    // Placeholder to execute when database is created (oldVersion is 0)
                    case 1:
                        // Create a store of objects
                        const store1 = db.createObjectStore('stazioni', {
                            // The `id` property of the object will be the key, and be incremented automatically
                            autoIncrement: true,
                            keyPath: 'id'
                        });
                        setupProgress += 2;
                        loadingProgress += 2;
                        const store2 = db.createObjectStore('sensori', {
                            // The `id` property of the object will be the key, and be incremented automatically
                            autoIncrement: true,
                            keyPath: 'id'
                        });
                        setupProgress += 2;
                        loadingProgress += 2;
                        const store3 = db.createObjectStore('note', {
                            // The `id` property of the object will be the key, and be incremented automatically
                            autoIncrement: true,
                            keyPath: 'id'
                        });
                        setupProgress += 2;
                        loadingProgress += 2;
                        const store4 = db.createObjectStore('noteMeteo', {
                            // The `id` property of the object will be the key, and be incremented automatically
                            autoIncrement: true,
                            keyPath: 'id'
                        });
                        setupProgress += 2;
                        loadingProgress += 2;
                        const store5 = db.createObjectStore('noteDeflussiMinimi', {
                            // The `id` property of the object will be the key, and be incremented automatically
                            autoIncrement: true,
                            keyPath: 'id'
                        });
                        setupProgress += 2;
                        loadingProgress += 2;
                        const store6 = db.createObjectStore('noteLimnimetri', {
                            // The `id` property of the object will be the key, and be incremented automatically
                            autoIncrement: true,
                            keyPath: 'id'
                        });
                        setupProgress += 2;
                        loadingProgress += 2;
                    // Create an index called `name` based on the `type` property of objects in the store
                    //store.createIndex('type', 'type');
                }
            }
        });
        setupProgress += 2;
        const db2 = await openDB('lastUpdate', 1, {
            upgrade(db, oldVersion, newVersion, transaction) {
                // Switch over the oldVersion, *without breaks*, to allow the database to be incrementally upgraded.
                switch(oldVersion) {
                    case 0:
                    // Placeholder to execute when database is created (oldVersion is 0)
                    case 1:
                        // Create a store of objects
                        const store = db.createObjectStore('date', {
                            // The `id` property of the object will be the key, and be incremented automatically
                            autoIncrement: true,
                            keyPath: 'id'
                        });
                        setupProgress += 2;
                }
            }
        });

        const db3 = await openDB('offline', 1, {
            upgrade(db, oldVersion, newVersion, transaction) {
                // Switch over the oldVersion, *without breaks*, to allow the database to be incrementally upgraded.
                switch(oldVersion) {
                    case 0:
                    // Placeholder to execute when database is created (oldVersion is 0)
                    case 1:
                        // Create a store of objects
                        const store1 = db.createObjectStore('stazioni', {
                            // The `id` property of the object will be the key, and be incremented automatically
                            autoIncrement: true,
                            keyPath: 'id'
                        });
                        const store2 = db.createObjectStore('notes', {
                            // The `id` property of the object will be the key, and be incremented automatically
                            autoIncrement: true,
                            keyPath: 'id'
                        });
                        const store3 = db.createObjectStore('notesMeteo', {
                            // The `id` property of the object will be the key, and be incremented automatically
                            autoIncrement: true,
                            keyPath: 'id'
                        });
                        const store4 = db.createObjectStore('notesDeflussiMinimi', {
                            // The `id` property of the object will be the key, and be incremented automatically
                            autoIncrement: true,
                            keyPath: 'id'
                        });
                        const store5 = db.createObjectStore('notesLimnimetri', {
                            // The `id` property of the object will be the key, and be incremented automatically
                            autoIncrement: true,
                            keyPath: 'id'
                        });
                        const store6 = db.createObjectStore('avvisi', {
                            // The `id` property of the object will be the key, and be incremented automatically
                            autoIncrement: true,
                            keyPath: 'id'
                        });
                        setupProgress += 2;
                }
            }
        });

        setupProgress += 2;
        loadingProgress += 2;
    }


    async function deleteDB(){
        const request = indexedDB.deleteDatabase("notes");
    }

    async function checkForOfflineData(){

        //STAZIONI
        const db = await openDB('offline');
        const tx = await db.transaction('stazioni', 'readonly');
        const store = tx.objectStore('stazioni');
        const stazioniOffline = await store.get(1);
        console.log("Offline Station to update: ", stazioniOffline.offline)

        if(stazioniOffline.offline === true){
            await uploadOfflineStazioni()
        }

        //AVVISI
        const tx3 = await db.transaction('avvisi', 'readonly');
        const store3 = tx3.objectStore('avvisi');
        const avvisiOffline = await store3.get(1);
        console.log("Offline Avvisi to update: ", avvisiOffline.offline)

        if(avvisiOffline.offline === true){
            await uploadAvvisiOffline()
        }

        //NOTES
        const tx2 = await db.transaction('notes', 'readonly');
        const store2 = tx2.objectStore('notes');
        const noteOffline = await store2.get(1);
        console.log("Offline Notes to update: ", noteOffline.offline)
        db.close();

        if(noteOffline.offline === true){
            await uploadOfflineNotes()
        }

        return new Promise((resolve, reject) => { // (*)
            setTimeout(() => resolve(1), 100);
        });
    }



    async function getAllStations() {
        const db = await openDB('notes');
        const tx = await db.transaction('stazioni', 'readonly');
        const store = tx.objectStore('stazioni');
        const value = await store.getAll();
        console.log("All Meteo Stations: ", value)
        await tx.done;
        db.close();
        return value;
    }

    async function getAllNotes() {
        const db = await openDB('notes');
        const tx = await db.transaction('note', 'readonly');
        const store = tx.objectStore('note');
        const value = await store.getAll();
        console.log("All Notes: ", value)
        await tx.done;
        db.close();
        return value;
    }

    async function getAllMeteoNotes() {
        const db = await openDB('notes');
        const tx = await db.transaction('noteMeteo', 'readonly');
        const store = tx.objectStore('noteMeteo');
        const value = await store.getAll();
        console.log("All Meteo Notes: ", value)
        await tx.done;
        db.close();
        return value;
    }

    async function getAllLimnimetriNotes() {
        const db = await openDB('notes');
        const tx = await db.transaction('noteLimnimetri', 'readonly');
        const store = tx.objectStore('noteLimnimetri');
        const value = await store.getAll();
        console.log("All Limnimetri Notes: ", value)
        await tx.done;
        db.close();
        return value;
    }

    async function getAllDeflussiMinimiNotes() {
        const db = await openDB('notes');
        const tx = await db.transaction('noteDeflussiMinimi', 'readonly');
        const store = tx.objectStore('noteDeflussiMinimi');
        const value = await store.getAll();
        console.log("All Limnimetri Notes: ", value)
        await tx.done;
        db.close();
        return value;
    }


    async function uploadAvvisiOffline(){
        let stations = await getAllStations();
        const dataToSend = stations.filter(function (n) {
            return n.avvisiOffline === true
        })

        for(const item of dataToSend){
            console.log("AVVISO TO SEND: ", item.avvisi, item.id)
            const dataToSend = JSON.stringify({"id": item.id, "avvisi": item.avvisi});
            //console.log("DATA TO SEND TO AVVISI", dataToSend)
            let dataReceived;
            fetch("/avviso", {
                credentials: "same-origin",
                mode: "same-origin",
                method: "post",
                headers: { "Content-Type": "application/json" },
                body: dataToSend
            })
                .then(async resp => {
                    if (resp.status === 200) {

                        return resp.json()
                    } else {
                        console.log("Status: " + resp.status)
                        return Promise.reject("server")
                    }
                })
                .then(async dataJson => {
                    dataReceived = dataJson
                    console.log("DATA RECEIVED FROM POST TO AVVISI: ",dataReceived)


                }).then(r => {
            })
                .catch(err => {
                    if (err === "server") return
                    console.log(err)
                })
        }



        return new Promise((resolve, reject) => { // (*)
            setTimeout(() => resolve(1), 100);
        });
    }


    async function uploadOfflineStazioni(){
        let stations = await getAllStations();
        const dataToSend = stations.filter(function (n) {
            return n.offline === true
        })

        console.log("ALL OFFLINE STATIONS TO ADD ", dataToSend);

        for (const item of dataToSend) {
            let dataReceived;
            fetch("/stazioni", {
                credentials: "same-origin",
                mode: "same-origin",
                method: "post",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(item)
            }).then(async resp => {
                    if (resp.status === 200) {
                        return resp.json()
                    } else {
                        console.log("Status: " + resp.status)
                        return Promise.reject("server")
                    }
                })
                .then(async dataJson => {
                    //console.log(dataJson)
                    dataReceived = dataJson
                    console.log("DATA RECEIVED FROM POST TO STAZIONI: ",dataReceived)



                }).then(r => {
                //console.log(dataJson)

            })
                .catch(err => {
                    if (err === "server") return
                    console.log(err)
                })
        }


        return new Promise((resolve, reject) => { // (*)
            setTimeout(() => resolve(1), 100);
        });
    }

    async function uploadOfflineNotes(){
        ///////////CHECK WHICH TYPES OF NOTES ARE OFFLINE THEN UPLOAD EVERYTHING
        //////MAYBE DO WITHOUT COPY PASTING CODE
        let allNotes = await getAllNotes();

        const db = await openDB('offline');
        const tx = await db.transaction('notesMeteo', 'readonly');
        const store = tx.objectStore('notesMeteo');
        const noteMeteoOffline = await store.get(1);
        await tx.done;
        console.log("Offline MeteoNotes to update: ", noteMeteoOffline.offline)
        const tx2 = await db.transaction('notesLimnimetri', 'readonly');
        const store2 = tx2.objectStore('notesLimnimetri');
        const noteLimnimetriOffline = await store2.get(1);
        await tx2.done;
        console.log("Offline Limnimetri to update: ", noteLimnimetriOffline.offline)
        const tx3 = await db.transaction('notesDeflussiMinimi', 'readonly');
        const store3 = tx3.objectStore('notesDeflussiMinimi');
        const noteDeflussiMinimiOffline = await store3.get(1);
        await tx3.done;
        console.log("Offline DeflussiMinimi to update: ", noteDeflussiMinimiOffline.offline)

        if(noteMeteoOffline.offline === true){
            let allMeteoNotes = await getAllMeteoNotes();
            const meteoNotesToSend = allMeteoNotes.filter(function (n) {
                return n.offline === true
            })
            console.log("ALL OFFLINE METEO NOTES TO ADD ", meteoNotesToSend);

            for (const item of meteoNotesToSend) {
                const note = allNotes.find(n => n.id === item.note_id)

                const data = {}
                data.noteMeteo=item;
                data.note=note;
                console.log("DATA TO SEND: ", data);

                await sendNotes(data, "/noteMeteo");
            }

            const tx4 = await db.transaction('notesMeteo', 'readwrite');
            const store4 = tx4.objectStore('notesMeteo');
            store4.put({id: 1, offline:false});
            await tx4.done;
        }

        const txx = await db.transaction('notes', 'readwrite');
        const storex = txx.objectStore('notes');
        storex.put({id: 1, offline:false});
        await txx.done;
        db.close()

        return new Promise((resolve, reject) => { // (*)
            setTimeout(() => resolve(1), 100);
        });
    }

    async function sendNotes(data, url){
        let dataReceived;
        fetch(url, {
            credentials: "same-origin",
            mode: "same-origin",
            method: "post",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        }).then(async resp => {
            if (resp.status === 200) {
                return resp.json()
            } else {
                console.log("Status: " + resp.status)
                return Promise.reject("server")
            }
        })
            .then(async dataJson => {
                //console.log(dataJson)
                dataReceived = dataJson
                console.log("DATA RECEIVED FROM POST TO ", url , ": ",dataReceived)


            }).then(r => {
            //console.log(dataJson)

        })
            .catch(err => {
                if (err === "server") return
                console.log(err)
            })

        return new Promise((resolve, reject) => { // (*)
            setTimeout(() => resolve(1), 100);
        });
    }

    async function checkIfDBExists()
    {
        let dbExists = true;

        const db = await openDB('lastUpdate');

        try {
            const tx = await db.transaction('date', 'readonly');
            const store = tx.objectStore('date');
            const value = await store.get([1]);
            console.log(value)
        }catch {
            indexedDB.deleteDatabase("lastUpdate");
            dbExists = false;

        }
        db.close();
        return dbExists;
    }


    async function dataBaseInit(){

        setupProgress += 10;

        const dbExists = await checkIfDBExists();
        console.log(dbExists)
        if(dbExists === false){
            setupProgress += 10;

            console.log("DB DOES NOT EXIST YET")
            await createDB().then(r => insertFirstDate()).then(r => checkForUpdate());
        }else{
            console.log("DB DOES EXIST")
            setupProgress += 40;

            if(await checkOnlineStatus() )
               await checkForOfflineData().then(r=> checkForUpdate().then(r => console.log("Finished DB Setup")));
            else{
                loadingProgress = setupProgress = 100;
                finishedSetUp = true;
            }
        }
    }

    async function insertFirstDate(){
        const db3 = await openDB('lastUpdate', 1);
        const tx = await db3.transaction('date', 'readwrite');
        const store = tx.objectStore('date');
        const dateJson = JSON.stringify(new Date('1997-08-07'));
        store.add({date: dateJson});
        await tx.done;
        setupProgress += 10;

    }


    async function checkForUpdate(){
        setupProgress += 10;
        getLastremoteUpdate().then(async function (result) {
            const lastRemoteDate = new Date(Date.parse(result.date))
            console.log("Last remote update: ", lastRemoteDate)
            const lastLocal =  await getLastLocalUpdate()
            const tmp = lastLocal.date.replace("\"", "").replace("\"", "")
            const lastLocalDate = new Date(tmp)
            console.log("Last local update: ", lastLocalDate)

            if (lastLocalDate < lastRemoteDate) {
                setupProgress += 10;
                console.log("Update required: ")
                await updateDB();
                console.log("FINISHED UPDATING DB")
                setupProgress = 100;
                loadingProgress = 100;
                finishedSetUp = true

            } else {
                setupProgress = 100;
                loadingProgress = 100;
                finishedSetUp = true;
                console.log("NO UPDATE NECESSARY")
            }
        }, failtureCallback)
    }

    async function getLastremoteUpdate(){
        return fetchAsync("/lastUpdate");
    }

    async function getLastLocalUpdate(){
        const db = await openDB('lastUpdate', 1);

        const value = await db.get('date', 1);

        return value
    }



    async function updateDB(){
       return new Promise(function (resolve, reject){
            setTimeout(() => resolve(1), 10); // (*)

        }).then(function(result){
            deleteDB();
            loadingProgress += 10;
           return new Promise((resolve, reject) => { // (*)
               setTimeout(() => resolve(result * 2), 100);
           });
        }).then(function(result){
            createDB();
           loadingProgress += 10;
           return new Promise((resolve, reject) => { // (*)
               setTimeout(() => resolve(result * 2), 100);
           });
        }).then(function(result){
            updateStazioniDB();
           loadingProgress += 10;
           return new Promise((resolve, reject) => { // (*)
               setTimeout(() => resolve(result * 2), 100);
           });
        }).then(function(result){
            updateSensoriDB();
           loadingProgress += 10;
           return new Promise((resolve, reject) => { // (*)
               setTimeout(() => resolve(result * 2), 100);
           });
        }).then(function(result){
            updateNoteDB();
           loadingProgress += 10;
           return new Promise((resolve, reject) => { // (*)
               setTimeout(() => resolve(result * 2), 100);
           });
        }).then(function(result){
            updateNoteDeflussiDB();
           loadingProgress += 10;
           setupProgress = 80;
           return new Promise((resolve, reject) => { // (*)
               setTimeout(() => resolve(result * 2), 100);
           });
        }).then(function(result){
            updateNoteLimnimetriDB();
           loadingProgress += 5;
           return new Promise((resolve, reject) => { // (*)
               setTimeout(() => resolve(result * 2), 100);
           });
        }).then(function(result){
            updateNoteMeteoDB();
           loadingProgress += 5;
           setupProgress = 90;
           return new Promise((resolve, reject) => { // (*)
               setTimeout(() => resolve(result * 2), 100);
           });
        }).then(function(result){
            updateLocalRemoteUpdateTimeDB();
           loadingProgress += 5;
           return new Promise((resolve, reject) => { // (*)
               setTimeout(() => resolve(result * 2), 100);
           });
        }).then(function(result){
           updateOfflineDB();
           loadingProgress += 5;
           return new Promise((resolve, reject) => { // (*)
               setTimeout(() => resolve(result * 2), 100);
           });
       }).then(function(result){
            updateNoteLimnimetriDB();
            loadingProgress += 5;
            setupProgress = 100;
           return new Promise((resolve, reject) => { // (*)
               setTimeout(() => resolve(result * 2), 100);
           });
        })

    }

    async function updateRemoteLastUpdate(){
        fetch("/lastUpdate", {
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            body: ""
        }).then(res => {
            console.log("Request complete! response:", res);
        });
    }

    async function updateStazioniDB(){
        fetch("/stazioni").then(function(response) {
            return response.json();
        }).then(async function (data) {
            const db = await openDB('notes', 1);
            const tx = await db.transaction('stazioni', 'readwrite');
            const store = tx.objectStore('stazioni');
            data.stazioni.forEach(e => store.add(e))
            //store.add(data.stazioni);
            await tx.done;

            console.log(data);
        }).catch(err => {
            console.error('error: ', err);
        });
    }

    async function updateSensoriDB(){
        fetch("/sensori").then(function(response) {
            return response.json();
        }).then(async function (data) {
            const db = await openDB('notes', 1);
            const tx = await db.transaction('sensori', 'readwrite');
            const store = tx.objectStore('sensori');
            data.sensori.forEach(e => store.add(e))
            await tx.done;

            console.log(data);
        }).catch(err => {
            console.error('error: ', err);
        });

    }

    async function updateNoteDB(){
        fetch("/note").then(function(response) {
            return response.json();
        }).then(async function (data) {
            const db = await openDB('notes', 1);
            const tx = await db.transaction('note', 'readwrite');
            const store = tx.objectStore('note');
            data.note.forEach(e => store.add(e))
            await tx.done;
            console.log(data);
        }).catch(err => {
            console.error('error: ', err);
        });

    }

    async function updateNoteDeflussiDB(){
        fetch("/noteDeflussiMinimi").then(function(response) {
            return response.json();
        }).then(async function (data) {
            const db = await openDB('notes', 1);
            const tx = await db.transaction('noteDeflussiMinimi', 'readwrite');
            const store = tx.objectStore('noteDeflussiMinimi');
            data.noteDeflussiMinimi.forEach(e => store.add(e))
            await tx.done;
            console.log(data);
        }).catch(err => {
            console.error('error: ', err);
        });

    }

    async function updateNoteLimnimetriDB(){
        fetch("/noteLimnimetri").then(function(response) {
            return response.json();
        }).then(async function (data) {
            const db = await openDB('notes', 1);
            const tx = await db.transaction('noteLimnimetri', 'readwrite');
            const store = tx.objectStore('noteLimnimetri');
            data.noteLimnimetri.forEach(e => store.add(e))
            await tx.done;
            console.log(data);
        }).catch(err => {
            console.error('error: ', err);
        });

    }

    async function updateNoteMeteoDB(){
        fetch("/noteMeteo").then(function(response) {
            return response.json();
        }).then(async function (data) {
            const db = await openDB('notes', 1);
            const tx = await db.transaction('noteMeteo', 'readwrite');
            const store = tx.objectStore('noteMeteo');
            data.noteMeteo.forEach(e => store.add(e))
            await tx.done;
            console.log(data);
        }).catch(err => {
            console.error('error: ', err);
        });

    }

    async function updateOther(){

    }

    async function updateLocalRemoteUpdateTimeDB(){
        const db3 = await openDB('lastUpdate', 1);
        const tx = await db3.transaction('date', 'readwrite');
        const store = tx.objectStore('date');
        const dateJson = JSON.stringify(new Date());
        store.put({id: 1, date: dateJson});
        await tx.done;
        db3.close()
    }

    async function updateOfflineDB(){
        const db3 = await openDB('offline', 1);
        const tx = await db3.transaction('stazioni', 'readwrite');
        const store = tx.objectStore('stazioni');
        store.put({id: 1, offline:false});
        await tx.done;

        const tx2 = await db3.transaction('notes', 'readwrite');
        const store2 = tx2.objectStore('notes');
        store2.put({id: 1, offline:false});
        await tx2.done;

        const tx3 = await db3.transaction('notesMeteo', 'readwrite');
        const store3 = tx3.objectStore('notesMeteo');
        store3.put({id: 1, offline:false});
        await tx3.done;

        const tx4 = await db3.transaction('notesLimnimetri', 'readwrite');
        const store4 = tx4.objectStore('notesLimnimetri');
        store4.put({id: 1, offline:false});
        await tx4.done;

        const tx5 = await db3.transaction('notesDeflussiMinimi', 'readwrite');
        const store5 = tx5.objectStore('notesDeflussiMinimi');
        store5.put({id: 1, offline:false});
        await tx5.done;

        const tx6 = await db3.transaction('avvisi', 'readwrite');
        const store6 = tx6.objectStore('avvisi');
        store6.put({id: 1, offline:false});
        await tx6.done;
        db3.close()
    }

    async function updateRemoteUpdate(){
        fetch("/lastUpdate", {
            method: "POST",
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        }).then(res => {
            console.log("Request complete! response:", res);
        }).catch(function() {
            console.log("Booo");
        });
    }


    let data = {element: "barium"};

    function failtureCallback(){
        console.log("FAILED")
    }

    async function fetchAsync (url) {
        let response = await fetch(url);
        let data = await response.json();
        return data;
    }

</script>

<link rel="apple-touch-icon" href="../public/images/icons/apple-touch-icon-512x512.png">

<meta name="theme-color" />
<meta name = "viewport" content = "width=device-width, minimum-scale=1.0, maximum-scale = 1.0, user-scalable = no">

<MaterialApp>
    <TabsBar
            bind:loadingProgress
            bind:setupProgress
            >
    </TabsBar>

    {#if finishedSetUp === true}
        <Windows
        >
        </Windows>
    {/if}
</MaterialApp>