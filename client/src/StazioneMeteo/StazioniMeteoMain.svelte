<script>

    import {selectedMeteoStation, valueMeteo} from "../Stores/store.js";
    import { mobileMode } from "../Stores/store.js";
    import {
        ComposedModal,
        ModalHeader,
        ModalBody,
        ModalFooter,
        RadioButtonGroup,
        RadioButton,
        DataTableSkeleton,
        TileGroup, RadioTile, ButtonSet, Button, SkeletonPlaceholder, Tile, Search, Dropdown
    } from "carbon-components-svelte";
    import { TextInput,Tag  } from "carbon-components-svelte";
    import { DataTable, Toolbar, ToolbarContent, ToolbarSearch,} from "carbon-components-svelte";
    import { MaterialApp, Divider } from 'svelte-materialify';
    import Add from "carbon-icons-svelte/lib/Add.svelte";
    import {openDB} from "idb";
    import { online } from "../Stores/store.js";


    let stations = stationsMain()
    let selectedStation;
    let open = false;
    let name = "";
    let type = "meteoStation";
    let filter = "";
    let order = 0;


    window.setInterval(async function () {
        $online = await checkOnlineStatus();
        console.log("Checking online status: ", $online)

    }, 5000);

   // function checkOnlineStatus(){
    //    $online = navigator.onLine;
    ////    console.log("Checking online status: ", $online)
    //}

    const checkOnlineStatus = async () => {
        try {
            const online = await fetch("/testOnline");
            return online.status >= 200 && online.status < 300; // either true or false
        } catch (err) {
            return false; // definitely offline
        }
    };


    const pickStation = async (selected) => {
        if (selectedStation != null) {
            let tmp = await stations;
            let stat = tmp.filter(function (n) {
                return n.id === selected
            })

            console.log("STAT", stat)
            $selectedMeteoStation = stat[0];
            $valueMeteo = 1;
            //console.log(JSON.stringify($selectedMeteoStation, 0, 2))
        }
    }

    $: pickStation(selectedStation);
    $: console.log("selectedRowIds", selectedStation);
    $: stations = stationsMain($valueMeteo)
    $: stations = stationsMain(filter)
    $: stations = stationsMain(order)
    checkOnlineStatus()

    async function addNewMeteoStation() {
        if (await checkOnlineStatus()) {
            console.log("Adding new MeteoStation in ONLINE mode")
            addNewMeteoStationOnline()
        } else {
            console.log("Adding new MeteoStation in OFFLINE mode")
            addNewMeteoStationOffline()
        }

        name = ""
    }

    function addNewMeteoStationOnline(){
        const dataToSend = JSON.stringify({"name": name, "type": type});
        let dataReceived;
        fetch("/stazioni", {
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
                console.log("DATA RECEIVED FROM POST TO STAZIONI: ",dataReceived)

                const db = await openDB('notes', 1);
                const tx = await db.transaction('stazioni', 'readwrite');
                const store = tx.objectStore('stazioni');
                store.add(dataJson)
                await tx.done;
                stations = stationsMain()
                await updateRemoteLastUpdate()

            }).then(r => {
            //console.log(dataJson)

        })
            .catch(err => {
                if (err === "server") return
                console.log(err)
            })
    }

    async function addNewMeteoStationOffline() {
        const dataToSend = {
            "name": name,
            "type": type,
            "offline": true,
            "avvisi": ""
        };
        const db = await openDB('notes', 1);
        const tx = await db.transaction('stazioni', 'readwrite');
        const store = tx.objectStore('stazioni');
        store.add(dataToSend)
        await tx.done;
        db.close()

        const db2 = await openDB('offline', 1);
        const tx2 = await db2.transaction('stazioni', 'readwrite');
        const store2 = tx2.objectStore('stazioni');
        store2.put({id: 1, offline:true});
        await tx2.done;
        db2.close()

        stations = stationsMain()
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

    async function getMeteoStations() {
        const db = await openDB('notes');
        const tx = await db.transaction('stazioni', 'readonly');
        const store = tx.objectStore('stazioni');
        const value = await store.getAll();
        //console.log("All Meteo Stations: ", value)
        db.close();
        const meteo = value.filter(function (n){
            return n.tipo === "meteoStation"
        })

        const search = value.filter(function (n){
            return n.name.includes(filter)
        })

        return search;
    }

    function removeTime(date) {
        return new Date(
            date.getFullYear(),
            date.getMonth(),
            date.getDate()
        );
    }

    async function distanceInDays(id) {
        let tmp = await getMeteoStations();
        let stat = tmp.find(function (n) {
            return n.id === id
        })

        if(stat.lastNote === null)
            return "---"

        let date1 = removeTime(new Date(stat.lastNote))
        let date2 = removeTime(new Date())

        if(isNaN(date1))
            return "---"
        console.log("DAtes: ", date1, date2)
        let difference = date1.getTime() - date2.getTime();
        return Math.abs(Math.ceil(difference / (1000 * 3600 * 24)));
    }

    async function stationsMain() {
        console.log("UPDATING STATION LIST")
        let stats = await getMeteoStations()


        for (const r of stats) {
            if(r.dismesso === true)
                r.distanceInDays = "Dismesso"
            else
                r.distanceInDays = await distanceInDays(r.id);
        }


        let ordered = stats;
        console.log(order)
        switch (order){
            case 0:
                break;
            case 1:
                console.log("ordering by alpha")
                ordered = stats.sort(function (a, b) {
                    if(a.name < b.name)
                        return -1
                    else if(a.name > b.name)
                        return 1
                    else
                        return 0
                });
                break;
            case 2:
                let tmp = stats.sort(function (a, b) {
                    console.log(a.distanceInDays, b.distanceInDays)
                    if(a.distanceInDays === "---")
                        return 1
                    else if(b.distanceInDays === "---")
                        return -1
                    else if(a.distanceInDays > b.distanceInDays)
                        return -1
                    else if(a.distanceInDays < b.distanceInDays)
                        return 1
                    else
                        return 0
                });

                break;
            case 3:
                ordered = stats.sort(function (a, b) {
                    if(a.avvisi === "")
                        return 1
                    else if(b.avvisi === "")
                        return -1
                    else
                        return 0
                });
                break;
            default:
                break;
        }

        console.log("Seach: ", stats);
        console.log("Ordered: ", ordered)


        return stats
    }


    function getLastNote(a){

        if(!a.lastNote){
            return "---"
        }
        else{
            return new Date(a.lastNote).toLocaleDateString()
        }
    }

    function getDistanceInDays(a){
        if(!a.distanceInDays && a.distanceInDays !== 0)
            return "---"
        else
            return a.distanceInDays
    }

    function getAvvisi(a){
        if(!a.avvisi)
            return ""
        else
            return a.distanceInDays
    }


    function delay(time) {
        return new Promise(resolve => setTimeout(resolve, time));
    }



</script>

<MaterialApp>
    <div class="windowFix">
        {#if $mobileMode === true}
                <Tile>
                    <div class="bx--data-table-header">
                        <div class="content">
                            <div>
                                <h4 class="bx--data-table-header__title">Stazioni Meteo</h4>
                                <p class="bx--data-table-header__description">Tutte le stazioni meteo.</p>
                            </div>
                            <div class="center">
                                <Button icon={Add}  kind="tertiary" on:click={() => (open = true)}></Button>
                            </div>
                        </div>
                  </div>
                 <br>

                <br>
                  <Search bind:value={filter} placeholder="Cerca Stazione per nome..."/>
                    <Dropdown
                            titleText="Ordina per..."
                            bind:selectedId={order}
                            items={[
                            { id: 0, text: "Nessuno" },
                            { id: 1, text: "Alfabetico" },
                            { id: 2, text: "Distanza in giorni" },
                            { id: 3, text: "Avvisi" },
                          ]}
                    />
                </Tile>

                {#await stations}
                    <br>
                    <TileGroup>
                        <SkeletonPlaceholder style="height: 10rem; width: 100%;" />
                        <br>
                        <SkeletonPlaceholder style="height: 10rem; width: 100%;" />
                        <br>
                        <SkeletonPlaceholder style="height: 10rem; width: 100%;" />

                    </TileGroup>
                {:then stats}

                    <br>
                    <TileGroup  bind:selected={selectedStation}>
                    {#each stats as stat}

                        <RadioTile value={stat.id}>
                            <div class="content">
                                <div>
                                    <h4>{stat.name}</h4>
                                    <Divider />
                                    <br>
                                    Ultimo Intervento: {getLastNote(stat)}
                                    <br>
                                    Distanza in Giorni: {getDistanceInDays(stat)}
                                    {#if !stat.avvisi}
                                    {:else}
                                        <br>
                                        <br>
                                        <Divider />
                                        <br>
                                        <Tag type="red">{stat.avvisi}</Tag>
                                    {/if}
                                </div>
                                <div class="vertical-center rightAlign">
                                    <ButtonSet stacked>
                                        <Button iconDescription="Nuova Nota"
                                                on:click={async function (){
                                                    selectedStation = stat.id;
                                                    await delay(500)
                                                    $valueMeteo = 2
                                                }}
                                                icon={Add}/>
                                    </ButtonSet>
                                </div>
                            </div>
                        </RadioTile>
                        <br>
                    {/each}

                    </TileGroup>
                {:catch error}
                    <p style="color: red">{error.message}</p>
                {/await}

        {:else}

            <div class="center">

                <div >
                    {#await stations}
                        <RadioButtonGroup>
                            <DataTableSkeleton
                                    headers={[
                                        { value: "Nome" },
                                        { value: "Ultimo Intervento" , sort: false},
                                        { value: "Distanza in Giorni" },
                                        {value: "Avvisi"},
                                        { empty: true },
                                      ]}
                                        rows={10}
                                            />
                        </RadioButtonGroup>
                    {:then stat}
                        <RadioButtonGroup bind:selected={selectedStation}>
                            <DataTable
                                    sortable
                                    title="Stazioni Meteo"
                                    description="Tutte le stazioni meteo."
                                    headers={[
                                    { key: "name", value: "Nome" },
                                    {key: "lastNote", value: "Ultimo Intervento"},
                                    {key: "distanceInDays", value: "Distanza in Giorni"},
                                    {key: "avvisi", value: "Avvisi"}
                                  ]}
                                    rows={stat}
                                >
                                <Toolbar>
                                    <ToolbarContent>
                                        <ToolbarSearch persistent shouldFilterRows />

                                        <Button on:click={() => (open = true)}>Crea Nuova Stazione</Button>
                                    </ToolbarContent>
                                </Toolbar>

                                <svelte:fragment slot="cell" let:row let:cell>
                                    {#if cell.key === "name"}
                                        <div class="radioWrapper">
                                            <RadioButton labelText="{cell.value}" value="{row.id}" />
                                        </div>
                                    {:else if cell.key === "lastNote" }
                                        {getLastNote(row)}
                                    {:else if cell.key === "lastNoteDistance" }
                                        {#if cell.value !== null && !isNaN(cell.value) }
                                            {cell.value}
                                        {:else}
                                            ---
                                        {/if}
                                    {:else if cell.key === "avvisi" }
                                        {#if cell.value !== ""}
                                            <Tag type="red">{cell.value}</Tag>
                                        {:else }
                                            ---
                                        {/if}
                                    {:else}
                                        {cell.value}
                                    {/if}
                                </svelte:fragment>
                            </DataTable>
                        </RadioButtonGroup>
                    {:catch error}
                        <p style="color: red">{error.message}</p>
                    {/await}
                </div>
            </div>
        {/if}
    </div>
</MaterialApp>


<ComposedModal
        hasScrollingContent
        selectorPrimaryFocus="#stationName"
        bind:open
        on:submit={function (){
            open = false
            addNewMeteoStation();
            }}>
    <ModalHeader label="Stazione Meteo" title="Crea Nuova Stazione Meteo" />
    <ModalBody hasForm>
        <TextInput
                id="stationName"
                invalid={name.length === 0}
                invalidText="Nome non puo' essere vuoto."
                inline
                labelText="Nome"
                placeholder="Inserire nome..."
                bind:value={name} />
    </ModalBody>
    <ModalFooter
            primaryButtonDisabled={name.length === 0}
            primaryButtonText="Aggiungi Stazione Meteo"
            secondaryButtons={[{ text: "Cancel" }]}
            on:click:button--primary={({ detail }) => {

            }}
            on:click:button--secondary={({ detail }) => {
              if (detail.text === "Cancel") open = false;
            }}

            />
</ComposedModal>

<style>

.radioWrapper {
    display: flex;
    align-items: flex-start;
    justify-content: left;
    margin: 0;
}

.center {
    margin: auto;
    width: auto;

    padding: 10px;
    display: flex;
    justify-content: center;
}

.vertical-center {
    margin: 0;

}


.rightAlign {
    margin: auto;
    width: auto;

    padding: 10px;
    display: flex;
    justify-content: right;
}

.content {
    display: grid;
    grid-template-columns: 80% 20%;
    grid-column-gap: 0px;
}



</style>
