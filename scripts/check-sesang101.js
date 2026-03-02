const {createClient}=require('@supabase/supabase-js');
require('dotenv').config({path:'.env.local'});
const sb=createClient(process.env.NEXT_PUBLIC_SUPABASE_URL,process.env.SUPABASE_SERVICE_ROLE_KEY);

async function main(){
  // Get sesang101 channel
  const {data:channels}=await sb.from('influencer_channels').select('*');
  console.log('Channels:');
  channels.forEach(c=>console.log(`  ${c.id} | ${c.channel_name} | ${c.youtube_channel_id}`));
  
  // Get sesang101 videos
  const sesangChannel = channels.find(c=>c.channel_name && (c.channel_name.includes('세상') || c.channel_name.includes('Sesang') || c.channel_name.includes('sesang')));
  if(!sesangChannel){
    // Try all videos
    const {data:vids}=await sb.from('influencer_videos').select('id,video_id,title,published_at,channel_id').order('published_at',{ascending:false});
    console.log('\nAll videos:', vids.length);
    // Group by channel
    const byChannel={};
    vids.forEach(v=>{byChannel[v.channel_id]=(byChannel[v.channel_id]||0)+1;});
    console.log('\nVideos per channel:');
    Object.entries(byChannel).forEach(([k,v])=>console.log(`  ${k}: ${v}`));
    // Show date range per channel
    for(const [cid,cnt] of Object.entries(byChannel)){
      const channelVids = vids.filter(v=>v.channel_id===cid);
      const newest = channelVids[0];
      const oldest = channelVids[channelVids.length-1];
      console.log(`  ${cid}: ${oldest.published_at} ~ ${newest.published_at} (${cnt} vids)`);
    }
    return;
  }
  console.log('\nSesang channel:', sesangChannel.id, sesangChannel.channel_name);
}
main();
