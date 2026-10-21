const React=require("react"),RD=require("react-dom/server"),sharp=require("sharp"),fa=require("react-icons/fa");
const names=["FaTimesCircle","FaQuestionCircle","FaClock","FaSearch","FaCheck","FaExclamationTriangle","FaTicketAlt","FaClipboardList","FaMobileAlt","FaCodeBranch","FaCheckCircle","FaWrench","FaFileAlt","FaUserCheck","FaShieldAlt","FaLock","FaEye","FaBan","FaRobot","FaHistory","FaGlobeEurope","FaDollarSign","FaFlag"];
const colors=["FFFFFF","012E2B","02BA71"];
(async()=>{for(const n of names)for(const c of colors){
 const svg=RD.renderToStaticMarkup(React.createElement(fa[n],{color:"#"+c,size:"256"}));
 await sharp(Buffer.from(svg)).resize(256,256,{fit:"contain",background:{r:0,g:0,b:0,alpha:0}}).png().toFile(`icons/${n}_${c}.png`);}
 console.log("icons",names.length*colors.length);})();
