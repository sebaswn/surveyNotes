<script>
    import {note, valueMeteo} from "../Stores/store.js";
    import { selectedMeteoStation } from "../Stores/store.js";
    import { mobileMode } from "../Stores/store.js";
    import {
        Button,
        TextInput,
        MultiSelect,
        Toggle,
        Select,
        SelectItem,
        TextArea,
        ToastNotification,
    } from "carbon-components-svelte";
    import {
        Divider,
        ExpansionPanel,
        ExpansionPanels,
        MaterialApp,
    } from 'svelte-materialify';
    import "carbon-components-svelte/css/white.css";
    import {openDB} from "idb";
    import NumberInput from "../CustomNumberInput.svelte";


    const operators = [
        { id: 'Mat', text: 'Mat' },
        { id: 'RSi', text: 'RSi' },
        { id: 'MPo', text: 'MPo' },
    ]

    const lavori = [
        { id: 'Controllo', text: 'Controllo' },
        { id: 'Pulizia', text: 'Pulizia' },
        { id: 'DW Dati', text: 'DW Dati' },
    ]

    let value = [2];
    let disabled = true;
    let errorList = "Dati Mancanti: ";
    let toast = false;

    function toggle(n) {
        if (value.includes(n)) {
            value.splice(value.indexOf(n), 1);
        } else {
            value.push(n);
        }
        value = value;
        disabled = !disabled;
        $note.calibration = !$note.calibration
    }

    const checkOnlineStatus = async () => {
        try {
            const online = await fetch("/testOnline");
            return online.status >= 200 && online.status < 300; // either true or false
        } catch (err) {
            return false; // definitely offline
        }
    };

    function formCheck() {
        let valid = true;
        if($note.statePluv === "0"){
            valid = false;
            errorList = errorList + "- Stato Pluviometro -"
        }
        if($note.operators.length === 0 && $note.customOperators === ""){
            valid = false;
            errorList = errorList + "- Operatori -"
        }

        if($note.workDone.length === 0 && $note.otherWorkDone === ""){
            valid = false;
            errorList = errorList + "- Lavori Svolti -"
        }

        return valid;
    }


    async function addNewNote() {
        console.log("NEW NOTE DATA ", createNewNoteJSON());

        if (formCheck()) {
            if (await checkOnlineStatus()) {
                console.log("Adding new Note in ONLINE mode")
                addNewNoteOnline()
            } else {
                console.log("Adding new Note in OFFLINE mode")
                addNewNoteOffline()
            }
        } else {
            toast = true;
        }
    }

    function createNewNoteJSON(){
        const dataToSend = {note : {}, noteMeteo : {}};

        let dateTime = new Date($note.date + "T" + $note.time)
        dataToSend.note.date = dateTime;


        let operators = ""
        $note.operators.forEach(function (o,i){
            if(i == 0)
                operators = operators + o
            else
                operators = operators + "/" + o
        })

        if ($note.customOperators !== "")
            operators = operators + "/" + $note.customOperators
        dataToSend.note.operatori = operators


        let lavoriSvolti = ""
        $note.workDone.forEach(function (w,i){
            if(i === 0)
                lavoriSvolti = lavoriSvolti + w
            else
                lavoriSvolti = lavoriSvolti + ", " + w
        })
        if($note.calibration === true)
            lavoriSvolti = lavoriSvolti + ", " + " calibrazione";
        if($note.otherWorkDone !== "")
            lavoriSvolti = lavoriSvolti + ", " + $note.otherWorkDone;
        dataToSend.note.lavoriSvolti = lavoriSvolti;

        switch ($note.stateOtherSensors){
            case "0":
                break;
            case "1":
                dataToSend.note.statoAltriSensori = "Buono"
                break;
            case "2":
                dataToSend.note.statoAltriSensori = "Sporco"
                break;
            case "3":
                dataToSend.note.statoAltriSensori = "Otturato"
                break;
            default:
        }

        if($note.observations !== ""){
            dataToSend.note.osservazioni = $note.observations;
        }

        if($note.foto !== ""){
            dataToSend.note.foto = $note.foto
        }

        dataToSend.note.stazione_id = $selectedMeteoStation.id

        console.log("STATO PLUV", $note.statePluv)
        switch ($note.statePluv){
            case "0":
                break;
            case "1":
                console.log("STATO 1")
                dataToSend.noteMeteo.statoPluviometro = "Buono"
                break;
            case "2":
                dataToSend.noteMeteo.statoPluviometro = "Sporco"
                break;
            case "3":
                dataToSend.noteMeteo.statoPluviometro = "Otturato"
                break;
            default:
        }

        if($note.problems !== ""){
            dataToSend.noteMeteo.malfunzionamenti = $note.problems;
        }

        dataToSend.noteMeteo.calibration = $note.calibration
        if($note.calibration === true){
            dataToSend.noteMeteo.calRisoluzione = $note.risoluzione;
            dataToSend.noteMeteo.calVolumeAcqua = $note.volumeAcqua;
            dataToSend.noteMeteo.calSuperficieBocca = $note.superficieBocca;
            dataToSend.noteMeteo.calNozzle = $note.nozzle;
            dataToSend.noteMeteo.calNoImpulsiDovuti = $note.nImpulsiDovuti;
            dataToSend.noteMeteo.calNoImpulsiMisurati = $note.nImpulsiMisurati;
            dataToSend.noteMeteo.calPercentualeErrore = (($note.nImpulsiDovuti - $note.nImpulsiMisurati)/ $note.nImpulsiDovuti) * 100;
        }


        console.log("DATA TO SEND TO POST NEW METEO:", dataToSend)
        return { dataToSend };

    }

    function addNewNoteOnline(){
        let dataToSend = JSON.stringify(createNewNoteJSON());
        let dataReceived;
        fetch("/noteMeteo", {
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
                //console.log(dataJson)
                dataReceived = dataJson
                console.log("DATA RECEIVED FROM POST TO noteMeteo: ", dataReceived)

                const db = await openDB('notes', 1);
                const tx = await db.transaction('note', 'readwrite');
                const store = tx.objectStore('note');
                store.add(dataReceived.note);
                await tx.done;

                const tx2 = await db.transaction('noteMeteo', 'readwrite');
                const store2 = tx2.objectStore('noteMeteo');
                store2.add(dataReceived.noteMeteo);
                await tx2.done;


                const tx3 = await db.transaction('stazioni', 'readwrite');
                const store3 = tx3.objectStore('stazioni');
                let all = await store3.getAll()
                let st = all.find(el => el.id === $selectedMeteoStation.id);
                st.lastNote = dataReceived.note.date
                store3.put(st)
                db.close()

                //await updateRemoteLastUpdate()

                const notee = {
                    date: new Date().toISOString().slice(0, 10),
                    time: new Date().toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', hour12: false}),
                    operators: [],
                    customOperators: "",
                    statePluv: "",
                    stateOtherSensors: "",
                    workDone: [""],
                    observations: "",
                    calibration: false,
                    problems: "",
                    foto: ""
                }

                $note = notee

                $valueMeteo = 1

            }).then(r => {
            //console.log(dataJson)

        })
            .catch(err => {
                if (err === "server") return
                console.log(err)
            })
    }

    async function addNewNoteOffline() {
        let dataTMP = createNewNoteJSON();
        console.log(dataTMP)
        dataTMP.dataToSend.note.offline = true
        dataTMP.dataToSend.noteMeteo.offline = true
        let dataToSend = dataTMP.dataToSend
        console.log(dataToSend.note)


        const db = await openDB('notes', 1);
        const tx = await db.transaction('note', 'readwrite');
        const store = tx.objectStore('note');
        store.add(dataToSend.note)
        const id = await store.count()
        await tx.done;

        dataToSend.noteMeteo.note_id = id;
        console.log(dataToSend.noteMeteo)

        const tx2 = await db.transaction('noteMeteo', 'readwrite');
        const store2 = tx2.objectStore('noteMeteo');
        store2.add(dataToSend.noteMeteo)
        await tx2.done;

        const tx5 = await db.transaction('stazioni', 'readwrite');
        const store5 = tx5.objectStore('stazioni');
        let all = await store5.getAll()
        let st = all.find(el => el.id === $selectedMeteoStation.id);
        st.lastNote = dataToSend.note.date
        store5.put(st)
        db.close()

        const db2 = await openDB('offline', 1);
        const tx3 = await db2.transaction('notes', 'readwrite');
        const store3 = tx3.objectStore('notes');
        store3.put({id: 1, offline:true});
        await tx3.done;

        const tx4 = await db2.transaction('notesMeteo', 'readwrite');
        const store4 = tx4.objectStore('notesMeteo');
        store4.put({id: 1, offline:true});
        await tx4.done;
        db2.close()

        const notee = {
            date: new Date().toISOString().slice(0, 10),
            time: new Date().toLocaleTimeString([], {hour: '2-digit', minute: '2-digit', hour12: false}),
            operators: [],
            customOperators: "",
            statePluv: "",
            stateOtherSensors: "",
            workDone: [""],
            observations: "",
            calibration: false,
            problems: "",
            foto: ""
        }
        $note = notee
        $valueMeteo = 1
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



</script>



<MaterialApp>
    <div class="center">
        <div class="container">
            <form class:content="{!$mobileMode}" class:contentMobile="{$mobileMode}">
                <label>Data</label>
                <input type="date" bind:value={$note.date} />
                <Divider />
                <Divider />
                <label>Ora</label>
                <input type="time" bind:value={$note.time} />
                <Divider />
                <Divider />
                <label>Operatori</label>
                <MultiSelect
                        bind:selectedIds={$note.operators}
                        titleText="Operatori"
                        label="Seleziona Operatori..."
                        items={operators}
                        hideLabel
                        sortItem={()=> {}}
                        let:item
                        let:index ></MultiSelect>
                <div></div>
                <TextInput labelText="Altri Operatori" placeholder="Inserire altri operatori..." bind:value={$note.customOperators} />
                <Divider />
                <Divider />
                <label>Stato Pluviometro</label>
                <Select
                        labelText="Stato Pluviometro"
                        hideLabel
                        bind:selected={$note.statePluv}
                        required
                        on:change={(e) => console.log("value", e.detail)}
                        >
                    <SelectItem value="0" text="Seleziona stato" />
                    <SelectItem value="1" text="Buono" />
                    <SelectItem value="2" text="Sporco" />
                    <SelectItem value="3" text="Otturato" />

                </Select>

                <Divider />
                <Divider />
                <label>Stato Altri Sensori</label>
                <Select
                        labelText="Stato Altri Sensori"
                        hideLabel
                        bind:selected={$note.stateOtherSensors}
                        required
                        on:change={(e) => console.log("value", e.detail)}
                >
                    <SelectItem value="0" text="Seleziona stato" />
                    <SelectItem value="1" text="Buono" />
                    <SelectItem value="2" text="Sporco" />
                    <SelectItem value="3" text="Otturato" />

                </Select>
                <Divider />
                <Divider />
                <label>Lavoro Svolto</label>
                <MultiSelect bind:selectedIds={$note.workDone}
                             titleText="Lavori Svolti"
                             label="Seleziona Lavori Svolti..."
                             items={lavori}
                             hideLabel
                             sortItem={()=> {}}
                             let:item
                             let:index ></MultiSelect>
                <div></div>
                <TextInput bind:value={$note.otherWorkDone} labelText="Altri Lavori Svolti" placeholder="inserire altri lavori svolti..." />
                <Divider />
                <Divider />
                <label>Calibrazione</label>
                <Toggle on:toggle={()=> toggle(0)} labelText="Calibrazione eseguita"> <span slot="labelA">No</span>
                    <span slot="labelB" style="color: blue">Sì</span>
                </Toggle>
                <div></div>
                <ExpansionPanels {disabled} bind:value>
                    <ExpansionPanel>
              <span slot="header"> {#if disabled === true}
                           Calibrazione non eseguita
                        {:else if disabled === false}
                           Calibrazione
                        {/if}
                    </span>
                        <div class:calibrationContent="{!$mobileMode}" class:calibrationContentMobile="{$mobileMode}">
                            <Divider />
                            <Divider />
                            <label>Risoluzione</label>
                            <NumberInput inputmode="decimal" step={0.01} allowEmpty hideLabel label="Risoluzione" bind:value={$note.risoluzione}/>
                            <Divider />
                            <Divider />
                            <label>Volume Acqua</label>
                            <NumberInput inputmode="decimal" step={0.1} allowEmpty hideLabel label="Volume Acqua" bind:value={$note.volumeAcqua} />
                            <Divider />
                            <Divider />
                            <label>Superficie bocca</label>
                            <NumberInput inputmode="decimal" step={0.1} allowEmpty hideLabel label="Superficie bocca"  bind:value={$note.superficieBocca} />
                            <Divider />
                            <Divider />
                            <label>Nozzle</label>
                            <NumberInput inputmode="decimal" step={0.1} allowEmpty hideLabel label="Nozzle"  bind:value={$note.nozzle} />
                            <Divider />
                            <Divider />
                            <label>N° impulsi dovuti</label>
                            <NumberInput inputmode="decimal" step={0.1} allowEmpty hideLabel label="N° impulsi dovuti"  bind:value={$note.nImpulsiDovuti} />
                            <Divider />
                            <Divider />
                            <label>N° impulsi misurati</label>
                            <NumberInput inputmode="decimal" step={0.1} allowEmpty  hideLabel label="N° impulsi misurati"  bind:value={$note.nImpulsiMisurati}/>
                            <Divider />
                            <Divider />
                            <label>Errore</label>
                            <NumberInput inputmode="decimal" readonly hideLabel label="Errore"  value={ (($note.nImpulsiDovuti - $note.nImpulsiMisurati)/ $note.nImpulsiDovuti) * 100  }/>
                            <Divider />
                            <Divider />
                        </div>
                    </ExpansionPanel>
                </ExpansionPanels>
                <Divider />
                <Divider />
                <label>Osservazioni</label>
                <TextArea hidelabel placeholder="Osservazioni" bind:value={$note.observations}></TextArea>
                <Divider />
                <Divider />
                <label>Malfunzionamenti</label>
                <TextArea hidelabel placeholder="Malfunzionamenti" bind:value={$note.problems}></TextArea>
                <Divider />
                <Divider />
                <label>Foto</label>
                <input bind:value={$note.foto} type="file"
                       id="avatar" name="avatar"
                       accept="image/png, image/jpeg">
                <Divider />
                <Divider />
                <span></span>
                <Button  on:click={() => addNewNote()}   width="100%">Crea Nota</Button>
            </form>
        </div>
    </div>



    <br>
    <br>
    <br>
    <p>
        {JSON.stringify($note, 0, 2)}
    </p>
    <br>
    <br>
    <br>
    <br>
</MaterialApp>


{#if toast}
    <div class:toast="{!$mobileMode}" class:toastMobile="{$mobileMode}" class="center">
        <ToastNotification
            title="Mancano Dati non opzionali"
            kind="warning"
            subtitle="I dati non opzionali sono marcati con *"
            bind:caption={errorList}
            on:close={(e) => {
                e.preventDefault();
                toast = false;
                errorList = "Dati Mancanti: ";
            }
        }
        />
    </div>
{/if}

<style>
    .content {
        display: grid;
        grid-template-columns: 20% 80%;
        grid-column-gap: 0px;
        grid-row-gap: 10px;
        width: 50%;
        padding: 10px;
    }
    .container{
        width: 100%;
        padding: 10px;
        display: flex;
        justify-content: center;
    }

    .contentMobile {
        display: grid;
        grid-template-columns: 100%;
        grid-column-gap: 0px;
        grid-row-gap: 10px;
        width: 100%;
        padding: 0px;

    }

    .calibrationContent{
        display: grid;
        grid-template-columns: 20% 80%;
        grid-column-gap: 0px;
        grid-row-gap: 10px;
        width: 100%;
    }

    .calibrationContentMobile{
        display: grid;
        grid-template-columns: 100%;
        grid-column-gap: 0px;
        grid-row-gap: 10px;
        width: 100%;
    }

    .center {
        margin: auto;
        width: auto;

        padding: 10px;
        display: flex;
        justify-content: center;
    }

    .toast {
        position: fixed;
        top: 85%;
        left: 0;
        right: 0;
        width: 100%;
        display: flex;
        margin-top: 1rem;
        justify-content: center;
        z-index: 1000;
    }


    .toastMobile {
        position: fixed;
        top: 50%;
        left: 0;
        right: 0;
        width: 100%;
        display: flex;
        margin-top: 1rem;
        justify-content: center;
        z-index: 1000;
    }

</style>
