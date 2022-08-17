<script>
    import {
        DataTable,
        DataTableSkeleton,
        TextInput,
        Button,
        Grid,
        Row,
        Column,
        Tile,
        OverflowMenu,
        OverflowMenuItem,
        Modal,
        StructuredListHead,
        StructuredListRow,
        StructuredListCell,
        StructuredListBody,
        StructuredList, Link, ExpandableTile, Accordion, AccordionItem, TileGroup, SkeletonPlaceholder
    } from "carbon-components-svelte";
    import {Divider} from "svelte-materialify";

    import {openDB} from "idb";
    import {mobileMode, online, selectedMeteoStation, valueMeteo} from "../Stores/store";
    import Add from "carbon-icons-svelte/lib/Add.svelte";
    import TrashCan from "carbon-icons-svelte/lib/TrashCan.svelte";
    import AlignBoxTopLeft  from "carbon-icons-svelte/lib/AlignBoxTopLeft.svelte";
    import Edit from "carbon-icons-svelte/lib/Edit.svelte";
    import Close from "carbon-icons-svelte/lib/Close.svelte";
    import View from "carbon-icons-svelte/lib/View.svelte";


    let avvisi = ""

    let open = false;
    let calNoImpulsiDovuti = 0;
    let calNoImpulsiMisurati = 0;
    let calNozzle = 0;
    let calRisoluzione = 0;
    let calSuperficieBocca = 0;
    let calVolumeAcqua = 0;
    let calPercentualeErrore = 0;



    $: av($selectedMeteoStation.avvisi)
    $: allRelevantNotes = getNotes($selectedMeteoStation.id);
    $: allRelevantNotes = getNotes($valueMeteo);

    function av(){
        avvisi = $selectedMeteoStation.avvisi
    }


    const checkOnlineStatus = async () => {
        try {
            const online = await fetch("/testOnline");
            return online.status >= 200 && online.status < 300; // either true or false
        } catch (err) {
            return false; // definitely offline
        }
    };


    async function getNotes(id) {
        const db = await openDB('notes');
        const tx = await db.transaction('note', 'readonly');
        const store = tx.objectStore('note');
        const notes = await store.getAll();
        await tx.done;
        console.log("All Notes: ", notes)

        const tx2 = await db.transaction('noteMeteo', 'readonly');
        const store2 = tx2.objectStore('noteMeteo');
        const notesMeteo = await store2.getAll();
        await tx2.done;
        console.log("All NotesMeteo: ", notesMeteo)
        db.close();


        const filteredNotes = notes.filter(function (entry){

            return entry.stazione_id === $selectedMeteoStation.id;
        })
        console.log("STATION ID ", $selectedMeteoStation)

        let combinedNotes = [];
        filteredNotes.forEach(function (note,i){
            const noteMeteo = notesMeteo.find(el => el.note_id === note.id);

            const combined = {
                id: i,
                noteMeteo,
                note
            }
            combinedNotes.push(combined)

        })

        console.log("COMBINED ",(combinedNotes));
        return combinedNotes;
    }


    async function createAvvisoOnline(){
        const dataToSend = JSON.stringify({"id": $selectedMeteoStation.id, "avvisi": avvisi});
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

                const db = await openDB('notes', 1);
                const tx = await db.transaction('stazioni', 'readwrite');
                const store = tx.objectStore('stazioni');
                let all = await store.getAll()
                let st = all.find(el => el.id === $selectedMeteoStation.id);
                st.avvisi = avvisi
                store.put(dataReceived)
                await tx.done;
                $selectedMeteoStation = dataReceived
                //await updateRemoteLastUpdate()

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

    async function createAvvisoOffline(){
        const db = await openDB('notes', 1);
        const tx = await db.transaction('stazioni', 'readwrite');
        const store = tx.objectStore('stazioni');
        let all = await store.getAll()
        let st = all.find(el => el.id === $selectedMeteoStation.id);
        st.avvisi = avvisi
        st.avvisiOffline = true;
        store.put(st)
        await tx.done;
        $selectedMeteoStation = st

        const db2 = await openDB('offline', 1);
        const tx2 = await db2.transaction('avvisi', 'readwrite');
        const store2 = tx2.objectStore('avvisi');
        store2.put({id: 1, offline:true});
        await tx2.done;
        db2.close()

    }

    async function aggiornaAvviso(){
        if(await checkOnlineStatus()){
            console.log("Adding new MeteoStation in ONLINE mode")
            await createAvvisoOnline()
        }else {
            console.log("Adding new MeteoStation in OFFLINE mode")
            await createAvvisoOffline()
        }
    }

    function deleteAvviso(){
        avvisi = "";
        aggiornaAvviso();
    }

    async function showCalibration(id) {
        calRisoluzione = id.noteMeteo.calRisoluzione;
        calVolumeAcqua = id.noteMeteo.calVolumeAcqua;
        calSuperficieBocca = id.noteMeteo.calSuperficieBocca;
        calNozzle = id.noteMeteo.calNozzle;
        calNoImpulsiDovuti = id.noteMeteo.calNoImpulsiDovuti;
        calNoImpulsiMisurati = id.noteMeteo.calNoImpulsiMisurati;
        calPercentualeErrore = id.noteMeteo.calPercentualeErrore;

        open = true;
    }


</script>

{#if $mobileMode === true}

    {#await allRelevantNotes}
        <Tile>
            <Accordion skeleton count={2} />
        </Tile>
        <br>
        <TileGroup>
            <SkeletonPlaceholder style="height: 10rem; width: 100%;" />
            <br>
            <SkeletonPlaceholder style="height: 10rem; width: 100%;" />
            <br>
            <SkeletonPlaceholder style="height: 10rem; width: 100%;" />

        </TileGroup>
    {:then relNotes}
        <Tile>
            <Accordion>
                <AccordionItem open title="Avvisi">
                    <TextInput size="xl" bind:value={avvisi} placeholder="Inserire avvisi..." />

                    {#if avvisi !== $selectedMeteoStation.avvisi && avvisi !== ""}
                        <Button on:click={aggiornaAvviso}>Aggiorna Avviso</Button>
                    {:else if avvisi === $selectedMeteoStation.avvisi && avvisi !== ""}
                        <Button on:click={deleteAvviso} kind="danger">Cancella Avviso</Button>
                    {/if}
                </AccordionItem>
                <AccordionItem title="Impostazioni">
                    <div class="content">
                        <Button on:click={() => $valueMeteo = 2} kind="tertiary" icon={AlignBoxTopLeft}>Nuova Nota</Button>
                        <Divider/>
                        <Button icon={Add}>Aggiungi Sensore</Button>
                        <Divider/>
                        <Button disabled={!$online} kind="danger-tertiary" icon={Edit}>Modifica Stazione</Button>
                        <Divider/>
                        <Button disabled={!$online} kind="secondary" icon={Close}>Dismettere Stazione</Button>
                        <Divider/>
                        <Button disabled={!$online} icon={TrashCan} kind="danger">Elimina Stazione Meteo</Button>

                    </div>
                </AccordionItem>
            </Accordion>
        </Tile>
        <br>

        {#each relNotes as note}
            <Tile>
                <div>
                    <div>
                        <div class="contentTitle">
                            <p>{new Date(note.note.date).toLocaleDateString()}</p>

                            <p> - {note.note.operatori} </p>
                        </div>
                        <Divider />
                        <div class="info">
                            <p class="info">
                                <bo> Lavori Svolti: </bo> {note.note.lavoriSvolti}
                            </p>
                            {#if note.note.osservazioni}
                                <p class="info">
                                    <bo> Osservazioni: </bo> {note.note.osservazioni}
                                </p>
                            {/if}

                            {#if note.note.malfunzionamenti}
                                <p class="info">
                                    <bo> Malfunzionamenti: </bo> {note.note.malfunzionamenti}
                                </p>
                            {/if}
                        </div>
                        <Divider />
                        <p class="info">
                            <bo>Stato Pluviometro</bo>: {note.noteMeteo.statoPluviometro}
                        </p>

                        {#if note.note.statoAltriSensori}
                            <p class="info">
                                <bo>Stato Altri Sensori</bo>: {note.note.statoAltriSensori}
                            </p>
                        {/if}
                        <Divider />


                        {#if note.noteMeteo.calibrazione}
                            <Link on:click={()=> showCalibration(note)} icon={View}> Visualizza calibrazione </Link>
                        {/if}


                    </div>
                </div>
            </Tile>
            <br>
        {/each}

    {:catch error}
        <p style="color: red">{error.message}</p>
    {/await}

{:else}
    <Grid padding>
        <Row>
            <Column sm={12} md={12} lg={12}>

                <TextInput size="xl" labelText="Avvisi" bind:value={avvisi} placeholder="Inserire avvisi..." />

                {#if avvisi !== $selectedMeteoStation.avvisi && avvisi !== ""}
                    <Button on:click={aggiornaAvviso}>Aggiorna Avviso</Button>
                {:else if avvisi === $selectedMeteoStation.avvisi && avvisi !== ""}
                    <Button on:click={deleteAvviso} kind="danger">Cancella Avviso</Button>
                {/if}


                {#await allRelevantNotes}

                    <DataTableSkeleton
                            headers={[
                                {value: "Data"},
                                {value: "Operatori"},
                                {value: "Lavori Svolti"},
                                {value: "Stato Pluviometro"},
                                {value: "Stato Altri Sensori"},
                                {value: "Osservazioni" },
                                {value: "Malfunzionamenti" },
                              ]}
                            rows={10}
                    />

                {:then relNotes}
                    <DataTable
                            sortable
                            sortKey = "note.date"
                            sortDirection = "descending"
                            headers={[
                        { key: "note.date", value: "Data",sort: false},
                        { key: "note.operatori", value: "Operatori", sort: false },
                        { key: "note.lavoriSvolti", value: "Lavori Svolti" ,sort: false},
                        { key: "noteMeteo.calibrazione", value: "Calibrazione" ,sort: false},
                        { key: "noteMeteo.statoPluviometro", value: "Stato Pluviometro" ,sort: false},
                        { key: "note.statoAltriSensori", value: "Stato Altri Sensori" ,sort: false},
                        { key: "note.osservazioni", value: "Osservazioni" ,sort: false},
                        { key: "noteMeteo.malfunzionamenti", value: "Malfunzionamenti" ,sort: false},
                      ]}
                            rows={relNotes}
                    >

                        <svelte:fragment slot="cell" let:row let:cell>
                            {#if cell.key === "note.date"}
                                {new Date(cell.value).toLocaleDateString()}
                            {:else if cell.key === "noteMeteo.calibrazione"}
                                {#if cell.value === false}
                                    ---
                                {:else }

                                    <Button
                                            size="small"
                                            iconDescription="Visualizza Calibrazione"
                                            icon={View}
                                            kind="ghost"
                                            on:click={() => showCalibration(row)}
                                    />
                                {/if}

                            {:else }
                                {#if cell.value !== null && cell.value !== "" && cell.value !== undefined}
                                    {cell.value}
                                {:else }
                                    ---
                                {/if}
                            {/if}
                        </svelte:fragment>

                    </DataTable>
                {:catch error}
                    <p style="color: red">{error.message}</p>
                {/await}

            </Column>


            <Column sm={4} md={4} lg={4}>
            <Tile class="content">
                <div class="content">
                    <Button on:click={() => $valueMeteo = 2} kind="tertiary" icon={AlignBoxTopLeft}>Nuova Nota</Button>
                    <Divider/>
                    <Button icon={Add}>Aggiungi Sensore</Button>
                    <Divider/>
                    <Button disabled={!$online} kind="danger-tertiary" icon={Edit}>Modifica Stazione</Button>
                    <Divider/>
                    <Button disabled={!$online} kind="secondary" icon={Close}>Dismettere Stazione</Button>
                    <Divider/>
                    <Button disabled={!$online} icon={TrashCan} kind="danger">Elimina Stazione Meteo</Button>

                </div>
            </Tile>
            </Column>
        </Row>
    </Grid>
{/if}



<Modal passiveModal bind:open modalHeading="Dati Calibrazione" on:open on:close>
    <p>
        <StructuredList condensed>
            <StructuredListHead>
                <StructuredListRow head>
                    <StructuredListCell head>Attributo</StructuredListCell>
                    <StructuredListCell head>Valore</StructuredListCell>
                </StructuredListRow>
            </StructuredListHead>
            <StructuredListBody>
                <StructuredListRow>
                    <StructuredListCell >Risoluzione</StructuredListCell>
                    <StructuredListCell >{calRisoluzione}</StructuredListCell>
                </StructuredListRow>
                <StructuredListRow>
                    <StructuredListCell>Volume acqua</StructuredListCell>
                    <StructuredListCell>{calVolumeAcqua}</StructuredListCell>
                </StructuredListRow>
                <StructuredListRow>
                    <StructuredListCell>Superficie bocca</StructuredListCell>
                    <StructuredListCell>{calSuperficieBocca}</StructuredListCell>
                </StructuredListRow>
                <StructuredListRow>
                    <StructuredListCell>Nozzle</StructuredListCell>
                    <StructuredListCell>{calNozzle}</StructuredListCell>
                </StructuredListRow>
                <StructuredListRow>
                    <StructuredListCell>N° impulsi dovuti</StructuredListCell>
                    <StructuredListCell>{calNoImpulsiDovuti}</StructuredListCell>
                </StructuredListRow>
                <StructuredListRow>
                    <StructuredListCell>N° impulsi misurati</StructuredListCell>
                    <StructuredListCell>{calNoImpulsiMisurati}</StructuredListCell>
                </StructuredListRow>
                <StructuredListRow>
                    <StructuredListCell>% errore</StructuredListCell>
                    <StructuredListCell>{calPercentualeErrore}</StructuredListCell>
                </StructuredListRow>

            </StructuredListBody>
        </StructuredList>
    </p>
</Modal>

<style>
    .content {
        display: grid;
        grid-template-columns: 100%;
        grid-column-gap: 0px;
        grid-row-gap: 10px;
        width: 100%;
        padding: 10px;
    }

    .contentTitle {
        display: grid;
        grid-template-columns: 30% 70%;
        grid-column-gap: 0px;
        grid-row-gap: 10px;
        width: 100%;
        padding: 0px;
    }



    bo{
        font-weight:bold;
    }

    .info{
        font-size:14px;
    }


</style>






