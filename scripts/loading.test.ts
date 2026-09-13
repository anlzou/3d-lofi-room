import {test} from 'node:test';
import assert from 'node:assert/strict';
import {loadingProgress,loadStages} from '../src/loading.ts';

test('the loading bar counts downloads and stays honest without Content-Length',()=>{
  const progress=loadingProgress();
  assert.equal(progress.value(),0);
  assert(progress.estimate().total>5e6,'the estimate should cover the whole first paint');
  // A slow connection with a real Content-Length: the bar follows the bytes.
  progress.report('model',1.38e6,2.76e6);
  const half=progress.value();
  assert(half>0&&half<.3,`half the model should be a fifth of the way in, got ${half}`);
  // Another host sends no length at all: the nominal size keeps the bar moving.
  progress.report('model',2.76e6,0);
  assert(progress.value()>half);
  // Nothing ever runs backwards, even if a range request is retried.
  progress.report('model',1e6,0);
  assert(progress.value()>half);
  progress.done('decode');progress.done('lighting');progress.done('build');
  assert.equal(progress.value(),1);
});
test('every stage the bar knows about is labelled and counted',()=>{
  const progress=loadingProgress();
  const ids=new Set<string>();
  for(const stage of loadStages){
    ids.add(stage.id);
    assert(progress.label(stage.id).length>0);
    progress.report(stage.id,stage.bytes,stage.bytes);
  }
  assert.equal(ids.size,loadStages.length,'stage ids must be unique');
  assert.equal(progress.value(),1);
  assert.equal(progress.estimate().loaded,progress.estimate().total);
});
