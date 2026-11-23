import json

with open('data/canonical/canonical_jobs.jsonl', 'r', encoding='utf-8') as f:
    jobs = [json.loads(line)['content']['data'] for line in f]
uncertain_jobs = [j for j in jobs if j['category'] == 'UNCERTAIN']

# Let's inspect the remaining jobs that aren't in the major clusters above
handled_ids = {
    'job_1a388cef4b8843e0', 'job_799b4f210a0fa4ff', 'job_fc9648e35ba5db78', 'job_122d9b1a2804bf26',
    'job_a94dd6fdadc3d3dd', 'job_aa46581403b45706', 'job_1491ef1a44058319', 'job_269fbdaeeea8515a',
    'job_93e9a4b3fd1528a4', 'job_0720bc84679aeca7', 'job_4628c8bf8e5ebcb2', 'job_ddb8989279b2765a',
    'job_6808753b9abd122d', 'job_fc733b2e34ce7d90', 'job_46ed8ae5be510862', 'job_d6d446b7dbc88c38',
    'job_984f995d02d192a3', 'job_b5650f32784de67d', 'job_20389864f9cfdf4b', 'job_8dacf0db937b2f92',
    'job_ea151868d0cabf39', 'job_350a930679a271b8', 'job_293c05cfec50d0fb', 'job_f8fe86ec4cb87275',
    'job_ad0a653b919ed9e7', 'job_0eee96d8d91c0017', 'job_2ea929afcff1d70b', 'job_4370eb0694ede9e6',
    'job_b14e70ee758843ba', 'job_df65ec2483015bf8', 'job_2c0079996ca79a21', 'job_b8483b279f8b1669',
    'job_59c5ff9eb072325f', 'job_d43c7e175f82a591', 'job_b097510b7a51bd85', 'job_155ecf409c92d109',
    'job_907cb81c338cc0e6', 'job_f06483a2fc383131', 'job_7406a46fe9807699', 'job_a77def0795597e98',
    'job_648f158f553d107f', 'job_de6f6aa7ce17764e', 'job_a44db05da429e646', 'job_081d0829d645623f',
    'job_97a4f768e103b5e6', 'job_09183096da77cafc', 'job_94a95091e1f91f3f', 'job_935400d30ab051bd',
    'job_c98f4209b2130bc9', 'job_60dafe151b165555', 'job_a59e43af035571a3', 'job_d98ec925aa02009f',
    'job_bea17c7bbad33d34', 'job_ac1156091b8fe8bf', 'job_eda8631b57f83fae', 'job_e99d75c13a1f6076',
    'job_31f4574a32f241d3', 'job_730121592a7b12a1', 'job_5b6e705fdd8a3e45', 'job_c06cd7c18855728d',
    'job_3f4147f80f8eed20', 'job_a3045fdafbd0cec5', 'job_e1fe8c2686b89dd0', 'job_1f1af246cfd4743c',
    'job_1fe2be9f97ca745e', 'job_5451ae341bb01502', 'job_07d1b215cf73dcbf', 'job_e35a732584dd5a91',
    'job_5b060bf5f7cd0896', 'job_93cbaa791c40727a', 'job_5203749acf4b14e8', 'job_dca7b0b6a47a6b85',
    'job_3fcc05f52bb7f78a', 'job_9b103a8e3aaa6496', 'job_4f60bf9ee90d37a0', 'job_f50c741f0b32bd5a',
    'job_e47964df703c1efd', 'job_a9f504c73a7ccd14', 'job_b1aed918a2400f31', 'job_22fda7d0b92e76aa',
    'job_b4b51eae834bb973', 'job_68fc708b1be009aa', 'job_dfddb5a9a3650b41', 'job_fde4b60fcd5d454c',
    'job_7373d597c590014b', 'job_e8078287eb87dc0c', 'job_acaff5006553133c', 'job_5572db9983b165e3',
    'job_ed0544426f0efc0a', 'job_8b6a7fe68fff1038', 'job_9395ac8eab83c8a2', 'job_9e4923f4f61926ea',
    'job_c47c30b19b7a902d', 'job_eb34300548855d73', 'job_e1db5679287eaf9f', 'job_0b951decd01c2b26',
    'job_c94d6cb844402565', 'job_91933cd76e884191', 'job_d732380d4b5b6679', 'job_9d00f80e541e6fd1',
    'job_ae42444b365c6fd0', 'job_4514f88d9ec70693', 'job_a8419aebc82b1a00', 'job_8380c3e88e9c6584',
    'job_86c624e1dd2c299c', 'job_f758d5d0dfd3c148', 'job_7fa0c886847ad020', 'job_2d0fc63ff4419f55',
    'job_ab5ac1cc60164046', 'job_4293f2e4c2289620', 'job_0b52ba3fd883521c', 'job_7ff814cb58f1225d',
    'job_50d1df7084a06283', 'job_675a85266ca800bd', 'job_52cf5f192858c983', 'job_707a7ad52df07edf',
    'job_201518350968ce4f'
}

remaining = [j for j in uncertain_jobs if j['jobId'] not in handled_ids]
print(f"Total handled in list: {len(handled_ids)}")
print(f"Total remaining to inspect: {len(remaining)}")

for r in remaining:
    print(r['jobId'], r['companyName'], r['jobTitle'])
