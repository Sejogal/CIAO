import { useSyncExternalStore } from "react";

export type Role = "owner" | "admin" | "member" | "viewer";
export type Member = { id:string; name:string; email:string; role:Role };
export type Company = { id:string; name:string; description:string; members:Member[] };
export type Project = { id:string; name:string; description:string; companyId:string };
export type DeviceModel = "ESP32"|"ESP8266"|"Arduino"|"Raspberry Pi"|"Outro";
export type Device = { id:string; name:string; model:DeviceModel; serial:string; firmware:string; online:boolean; active:boolean; lastSeen:string; projectId:string; token:string };
export type Datastream = { id:string; deviceId:string; name:string; key:string; pin:string; kind:"sensor"|"atuador"; dataType:"number"|"boolean"; unit:string; min:number|null; max:number|null; active:boolean; value:number; history:number[] };
export type Automation = { id:string; name:string; datastreamId:string; op:">"|"<"|"="; threshold:number; action:string; active:boolean };
export type Notice = { id:string; text:string; time:string; level:"warning"|"destructive"|"info"; read:boolean };
export type User = { id:string; name:string; email:string; role:string };
export type State = { user:User|null; companies:Company[]; projects:Project[]; devices:Device[]; datastreams:Datastream[]; automations:Automation[]; notices:Notice[]; prefs:{push:boolean;email:boolean;offline:boolean;theme:"claro"|"escuro"|"sistema";apiUrl:string}; flash:string|null };

const h=(base:number,amp:number)=>Array.from({length:24},(_,i)=>+(base+Math.sin(i/3)*amp+(i%5)*amp*.1).toFixed(1));
const me:User={id:"usr_7f3a21",name:"Seth Lussueki",email:"seth@kiandalabs.ao",role:"Utilizador"};

const initial:State={
 user:me,
 companies:[
  {id:"kianda",name:"Kianda Labs",description:"Laboratório de inovação em Luanda",members:[
   {id:me.id,name:me.name,email:me.email,role:"owner"},{id:"usr_2b91",name:"Ana Mateus",email:"ana@kiandalabs.ao",role:"admin"},{id:"usr_88c0",name:"João Baptista",email:"joao@kiandalabs.ao",role:"member"}]},
  {id:"agro",name:"AgroTech Huambo",description:"Agricultura de precisão",members:[
   {id:"usr_51aa",name:"Marta Kiala",email:"marta@agrotech.ao",role:"owner"},{id:me.id,name:me.name,email:me.email,role:"admin"}]}
 ],
 projects:[
  {id:"estufa",name:"Estufa Inteligente",description:"Rega e clima automáticos",companyId:"agro"},
  {id:"energia",name:"Monitor de Energia",description:"Consumo elétrico do escritório",companyId:"kianda"},
  {id:"agua",name:"Tanque de Água",description:"Nível e bomba remota",companyId:"kianda"}],
 devices:[
  {id:"esp32-01",name:"Sensor Estufa A",model:"ESP32",serial:"CIAO-32A-0001",firmware:"1.2.0",online:true,active:true,lastSeen:"agora",projectId:"estufa",token:"ciao_tk_a81f20c9e4"},
  {id:"esp8266-02",name:"Sensor Estufa B",model:"ESP8266",serial:"CIAO-82B-0002",firmware:"1.1.4",online:false,active:true,lastSeen:"há 2 h",projectId:"estufa",token:"ciao_tk_b72d11a0f3"},
  {id:"esp32-03",name:"Quadro Elétrico",model:"ESP32",serial:"CIAO-32C-0003",firmware:"1.2.0",online:true,active:true,lastSeen:"agora",projectId:"energia",token:"ciao_tk_c63e02b1a2"},
  {id:"esp32-04",name:"Boia do Tanque",model:"ESP32",serial:"CIAO-32D-0004",firmware:"1.0.9",online:true,active:true,lastSeen:"há 1 min",projectId:"agua",token:"ciao_tk_d54f93c2b1"}],
 datastreams:[
  {id:"ds1",deviceId:"esp32-01",name:"Temperatura",key:"temperature",pin:"V0",kind:"sensor",dataType:"number",unit:"°C",min:0,max:50,active:true,value:28.4,history:h(27,2)},
  {id:"ds2",deviceId:"esp32-01",name:"Humidade",key:"humidity",pin:"V1",kind:"sensor",dataType:"number",unit:"%",min:0,max:100,active:true,value:64,history:h(62,6)},
  {id:"ds3",deviceId:"esp32-01",name:"Válvula de rega",key:"pump",pin:"V2",kind:"atuador",dataType:"boolean",unit:"",min:0,max:1,active:true,value:1,history:[]},
  {id:"ds4",deviceId:"esp8266-02",name:"Luminosidade",key:"light",pin:"V0",kind:"sensor",dataType:"number",unit:"lx",min:0,max:2000,active:true,value:820,history:h(800,120)},
  {id:"ds5",deviceId:"esp32-03",name:"Potência",key:"power",pin:"V0",kind:"sensor",dataType:"number",unit:"kW",min:0,max:10,active:true,value:3.2,history:h(3,.8)},
  {id:"ds6",deviceId:"esp32-03",name:"Iluminação",key:"lights",pin:"V1",kind:"atuador",dataType:"boolean",unit:"",min:0,max:1,active:true,value:0,history:[]},
  {id:"ds7",deviceId:"esp32-04",name:"Nível",key:"level",pin:"V0",kind:"sensor",dataType:"number",unit:"%",min:0,max:100,active:true,value:72,history:h(70,10)},
  {id:"ds8",deviceId:"esp32-04",name:"Bomba",key:"pump",pin:"V1",kind:"atuador",dataType:"boolean",unit:"",min:0,max:1,active:true,value:0,history:[]}],
 automations:[
  {id:"a1",name:"Rega quando seco",datastreamId:"ds2",op:"<",threshold:40,action:"Ligar Válvula de rega",active:true},
  {id:"a2",name:"Alerta de calor",datastreamId:"ds1",op:">",threshold:30,action:"Enviar notificação",active:false}],
 notices:[
  {id:"n1",text:"Temperatura acima de 28 °C na Estufa A",time:"há 15 min",level:"destructive",read:false},
  {id:"n2",text:"Sensor Estufa B está offline",time:"há 2 h",level:"warning",read:false},
  {id:"n3",text:"Ana Mateus juntou-se à Kianda Labs",time:"ontem",level:"info",read:true}],
 prefs:{push:true,email:false,offline:true,theme:"claro",apiUrl:"https://api.ciao.ao/api/v1"},flash:null
};

let state=initial;
const listeners=new Set<()=>void>();
const notifyListeners=()=>listeners.forEach(l=>l());
export const uid=()=>Math.random().toString(36).slice(2,10);
export const setState=(fn:(s:State)=>Partial<State>)=>{state={...state,...fn(state)};notifyListeners()};
export const useStore=()=>useSyncExternalStore(l=>(listeners.add(l),()=>listeners.delete(l)),()=>state,()=>initial);
export const notify=(msg:string)=>{setState(()=>({flash:msg}));setTimeout(()=>setState(s=>s.flash===msg?{flash:null}:{}),2200)};
const up=<T extends {id:string}>(list:T[],item:T)=>list.some(x=>x.id===item.id)?list.map(x=>x.id===item.id?item:x):[...list,item];

export const actions={
 login:(u:User)=>setState(()=>({user:u})),logout:()=>setState(()=>({user:null})),saveUser:(u:User)=>setState(()=>({user:u})),
 saveCompany:(c:Company)=>setState(s=>({companies:up(s.companies,c)})),saveProject:(p:Project)=>setState(s=>({projects:up(s.projects,p)})),
 saveDevice:(d:Device)=>setState(s=>({devices:up(s.devices,d)})),saveDatastream:(d:Datastream)=>setState(s=>({datastreams:up(s.datastreams,d)})),
 saveAutomation:(a:Automation)=>setState(s=>({automations:up(s.automations,a)})),
 setPrefs:(p:Partial<State["prefs"]>)=>setState(s=>({prefs:{...s.prefs,...p}})),
 readAll:()=>setState(s=>({notices:s.notices.map(n=>({...n,read:true}))})),
 deleteDatastream:(id:string)=>setState(s=>({datastreams:s.datastreams.filter(x=>x.id!==id)})),
 deleteAutomation:(id:string)=>setState(s=>({automations:s.automations.filter(x=>x.id!==id)})),
 deleteDevice:(id:string)=>setState(s=>({devices:s.devices.filter(d=>d.id!==id),datastreams:s.datastreams.filter(x=>x.deviceId!==id)})),
 deleteProject:(id:string)=>setState(s=>{const dids=s.devices.filter(d=>d.projectId===id).map(d=>d.id);return{projects:s.projects.filter(p=>p.id!==id),devices:s.devices.filter(d=>d.projectId!==id),datastreams:s.datastreams.filter(x=>!dids.includes(x.deviceId))}}),
 deleteCompany:(id:string)=>setState(s=>{const pids=s.projects.filter(p=>p.companyId===id).map(p=>p.id);const dids=s.devices.filter(d=>pids.includes(d.projectId)).map(d=>d.id);return{companies:s.companies.filter(c=>c.id!==id),projects:s.projects.filter(p=>!pids.includes(p.id)),devices:s.devices.filter(d=>!dids.includes(d.id)),datastreams:s.datastreams.filter(x=>!dids.includes(x.deviceId))}})
};
